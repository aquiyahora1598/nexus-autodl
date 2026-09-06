import random
import re
import sys
import os
import time
import shutil
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Optional, Dict, Tuple, List

import pyautogui
from PIL import UnidentifiedImageError
from PIL.Image import open as open_image
from PIL.ImageFile import ImageFile

# Enable DPI awareness on Windows to prevent screen scaling click offsets
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

# OpenCV integration with multi-scale matching support
has_cv2 = False
try:
    import cv2
    import numpy as np
    has_cv2 = True
except ImportError:
    has_cv2 = False

_INTEGER_PATTERN = re.compile("([0-9]+)")


def _human_sort(key: Any) -> Tuple[Any, ...]:
    return tuple(int(c) if c.isdigit() else c for c in _INTEGER_PATTERN.split(str(key)))


class NexusAutoDL:
    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._root.title("Nexus AutoDL - Autoclicker Wabbajack")
        self._root.geometry("520x580")
        self._root.resizable(False, False)
        self._root.configure(bg="#111827")  # Slate Dark

        # Speed Presets: (min_sec, max_sec, display_name)
        self._speed_presets = {
            "fast": (8.0, 11.0, "🚀 Rápido (8 - 11s)"),
            "normal": (15.0, 21.0, "⚡ Normal (15 - 21s)"),
            "slow": (43.0, 56.0, "🛡️ Lento (43 - 56s)"),
        }
        self._selected_speed = tk.StringVar(value="normal")  # Default to Normal

        # Fixed internal options (hidden from UI for maximum simplicity)
        self._confidence = 0.85  # 85% similarity threshold (prevents false positives on other words/boxes)
        self._grayscale = True
        self._multiscale = True
        self._return_mouse = True

        self._running = False
        self._search_phase = "scan"
        self._phase_start = 0.0
        self._last_log_time = 0.0
        self._timer_id: Optional[str] = None
        self._templates: Dict[str, ImageFile] = {}
        self._cached_scaled_templates: List[Tuple[str, float, Any, int, int, float, float]] = []

        self._setup_ui()
        self._load_templates()

    def _setup_ui(self) -> None:
        # Title & Subtitle Banner
        header = tk.Frame(self._root, bg="#1f2937", pady=15, padx=20)
        header.pack(fill="x")

        title_lbl = tk.Label(
            header,
            text="Nexus AutoDL",
            font=("Segoe UI", 18, "bold"),
            fg="#f9fafb",
            bg="#1f2937"
        )
        title_lbl.pack(anchor="w")

        # Container Frame
        main_container = tk.Frame(self._root, bg="#111827", padx=20, pady=15)
        main_container.pack(fill="both", expand=True)

        # Status Card
        status_card = tk.Frame(main_container, bg="#1f2937", padx=15, pady=12)
        status_card.pack(fill="x", pady=(0, 15))

        tk.Label(
            status_card,
            text="ESTADO DEL SERVICIO",
            font=("Segoe UI", 8, "bold"),
            fg="#9ca3af",
            bg="#1f2937"
        ).pack(anchor="w")

        self._status_lbl = tk.Label(
            status_card,
            text="● DETENIDO",
            font=("Segoe UI", 12, "bold"),
            fg="#ef4444",
            bg="#1f2937"
        )
        self._status_lbl.pack(anchor="w", pady=(2, 0))

        # Speed Selection Card
        speed_card = tk.Frame(main_container, bg="#1f2937", padx=15, pady=15)
        speed_card.pack(fill="x", pady=(0, 15))

        tk.Label(
            speed_card,
            text="VELOCIDAD DE DESCARGA (INTERVALO)",
            font=("Segoe UI", 9, "bold"),
            fg="#f9fafb",
            bg="#1f2937"
        ).pack(anchor="w", pady=(0, 10))

        speed_btn_frame = tk.Frame(speed_card, bg="#1f2937")
        speed_btn_frame.pack(fill="x")

        # Preset Speed Buttons
        self._speed_btns: Dict[str, tk.Button] = {}

        btn_configs = [
            ("fast", "🚀 Rápido\n(8 - 11s)", "#3b82f6"),
            ("normal", "⚡ Normal\n(15 - 21s)", "#10b981"),
            ("slow", "🛡️ Lento\n(43 - 56s)", "#f59e0b")
        ]

        for idx, (key, label_text, color) in enumerate(btn_configs):
            btn = tk.Button(
                speed_btn_frame,
                text=label_text,
                font=("Segoe UI", 9, "bold"),
                bg="#374151",
                fg="#d1d5db",
                activebackground=color,
                activeforeground="white",
                bd=0,
                relief="flat",
                cursor="hand2",
                pady=10,
                command=lambda k=key: self._set_speed_preset(k)
            )
            btn.grid(row=0, column=idx, padx=4, sticky="ew")
            speed_btn_frame.grid_columnconfigure(idx, weight=1)
            self._speed_btns[key] = btn

        self._update_speed_buttons_ui()

        # Action Button (Start / Stop)
        self._start_btn = tk.Button(
            main_container,
            text="▶ INICIAR AUTOCLICKER",
            font=("Segoe UI", 12, "bold"),
            bg="#10b981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            pady=12,
            command=self._toggle_running
        )
        self._start_btn.pack(fill="x", pady=(0, 15))

        # Bottom Frame: Templates info + Console Log
        info_frame = tk.Frame(main_container, bg="#111827")
        info_frame.pack(fill="x", pady=(0, 5))

        self._tmpl_lbl = tk.Label(
            info_frame,
            text="Plantillas cargadas: 0",
            font=("Segoe UI", 8),
            fg="#9ca3af",
            bg="#111827"
        )
        self._tmpl_lbl.pack(side="left")

        open_folder_btn = tk.Button(
            info_frame,
            text="📂 Abrir Carpeta de Plantillas",
            font=("Segoe UI", 8),
            bg="#374151",
            fg="#d1d5db",
            activebackground="#4b5563",
            activeforeground="white",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self._open_templates_folder
        )
        open_folder_btn.pack(side="right")

        # Console Log
        log_card = tk.Frame(main_container, bg="#1f2937", padx=10, pady=10)
        log_card.pack(fill="both", expand=True)

        self._log_text = tk.Text(
            log_card,
            wrap="none",
            font=("Consolas", 9),
            bg="#111827",
            fg="#d1d5db",
            bd=0,
            height=8
        )
        self._log_text.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(log_card, command=self._log_text.yview)
        sb.pack(side="right", fill="y")
        self._log_text.config(yscrollcommand=sb.set)

        self._log_text.tag_config("fatal", foreground="#ef4444")
        self._log_text.tag_config("info", foreground="#10b981")
        self._log_text.tag_config("click", foreground="#3b82f6", font=("Consolas", 9, "bold"))
        self._log_text.tag_config("timestamp", foreground="#6b7280")

        self._log("Sistema iniciado correctamente. Selecciona una velocidad y pulsa Iniciar.")

    def _set_speed_preset(self, speed_key: str) -> None:
        self._selected_speed.set(speed_key)
        self._update_speed_buttons_ui()
        min_s, max_s, name = self._speed_presets[speed_key]
        self._log(f"Modo seleccionado: {name}")

    def _update_speed_buttons_ui(self) -> None:
        current = self._selected_speed.get()
        colors = {
            "fast": "#3b82f6",
            "normal": "#10b981",
            "slow": "#f59e0b"
        }
        for key, btn in self._speed_btns.items():
            if key == current:
                btn.config(bg=colors[key], fg="white", font=("Segoe UI", 9, "bold"))
            else:
                btn.config(bg="#374151", fg="#9ca3af", font=("Segoe UI", 9))

    def _log(self, message: str, level: str = "info") -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._log_text.insert("end", f"[{timestamp}] ", "timestamp")
        self._log_text.insert("end", f"{message}\n", level)
        self._log_text.yview_moveto(1.0)

    def _open_templates_folder(self) -> None:
        local_dir = Path.cwd() / "templates"
        local_dir.mkdir(exist_ok=True)
        os.startfile(str(local_dir))

    def _load_templates(self) -> None:
        self._templates.clear()

        local_dir = Path.cwd() / "templates"
        local_dir.mkdir(exist_ok=True)

        bundled_dir = None
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            b_dir = Path(sys._MEIPASS) / "templates"
            if b_dir.exists():
                bundled_dir = b_dir

        # Auto-copy factory templates to local_dir if local_dir is empty
        if bundled_dir and len([p for p in local_dir.iterdir() if p.suffix.lower() in [".png", ".jpg", ".jpeg"]]) == 0:
            for f in bundled_dir.iterdir():
                if f.is_file() and f.suffix.lower() in [".png", ".jpg", ".jpeg"]:
                    try:
                        shutil.copy(f, local_dir / f.name)
                    except Exception:
                        pass

        # Load templates from local directory (user editable)
        for tmpl_path in sorted(
            (str(p) for p in local_dir.iterdir() if p.suffix.lower() in [".png", ".jpg", ".jpeg"]),
            key=_human_sort
        ):
            try:
                self._templates[tmpl_path] = open_image(tmpl_path)
            except Exception:
                pass

        # Also load from bundled directory if not present locally
        if bundled_dir:
            for tmpl_path in sorted(
                (str(p) for p in bundled_dir.iterdir() if p.suffix.lower() in [".png", ".jpg", ".jpeg"]),
                key=_human_sort
            ):
                name = Path(tmpl_path).name
                if not any(Path(k).name == name for k in self._templates.keys()):
                    try:
                        self._templates[tmpl_path] = open_image(tmpl_path)
                    except Exception:
                        pass

        count = len(self._templates)
        self._cached_scaled_templates.clear()

        if has_cv2:
            scales = [0.75, 0.85, 0.95, 1.0, 1.05, 1.15, 1.25, 1.35]
            for path, img in self._templates.items():
                try:
                    img_rgb = img.convert("RGB")
                    template_np = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_BGR2GRAY if self._grayscale else cv2.COLOR_BGR2RGB)
                    th, tw = template_np.shape[:2]
                    for scale in scales:
                        sw, sh = int(tw * scale), int(th * scale)
                        if sw < 10 or sh < 10:
                            continue
                        resized_tmpl = cv2.resize(template_np, (sw, sh), interpolation=cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC)
                        _, std_t = cv2.meanStdDev(resized_tmpl)
                        max_t = float(resized_tmpl.max())
                        min_std = float(std_t[0][0]) * 0.70
                        min_max_val = max_t * 0.75
                        self._cached_scaled_templates.append((path, scale, resized_tmpl, sw, sh, min_std, min_max_val))
                except Exception:
                    pass

        self._tmpl_lbl.config(text=f"Plantillas cargadas: {count} | Similitud: 85%")
        self._log(f"Se cargaron {count} plantillas de imagen (Similitud requerida: 85%).")

    def _toggle_running(self) -> None:
        if self._running:
            self._stop()
        else:
            self._start()

    def _start(self) -> None:
        self._load_templates()
        if len(self._templates) == 0:
            messagebox.showerror(
                "Sin Plantillas",
                "No se encontraron imágenes en la carpeta 'templates'. Agrega capturas del botón antes de iniciar."
            )
            return

        self._running = True
        self._search_phase = "scan"
        self._phase_start = time.time()
        self._last_log_time = 0.0
        self._start_btn.config(text="⏹ DETENER AUTOCLICKER", bg="#ef4444", activebackground="#dc2626")
        self._status_lbl.config(text="● BUSCANDO Y HACIENDO CLIC", fg="#10b981")
        
        speed_name = self._speed_presets[self._selected_speed.get()][2]
        self._log(f"Autoclicker INICIADO ({speed_name}).", level="click")
        self._loop()

    def _stop(self) -> None:
        self._running = False
        self._search_phase = "scan"
        if self._timer_id:
            self._root.after_cancel(self._timer_id)
            self._timer_id = None
        self._start_btn.config(text="▶ INICIAR AUTOCLICKER", bg="#10b981", activebackground="#059669")
        self._status_lbl.config(text="● DETENIDO", fg="#ef4444")
        self._log("Autoclicker DETENIDO.")

    def _perform_click(self, x: int, y: int) -> None:
        initial_pos = pyautogui.position()
        self._log(f"¡Clic realizado en ({x}, {y})!", level="click")
        pyautogui.click(x, y)
        if self._return_mouse:
            pyautogui.moveTo(initial_pos)

    def _match_image(self) -> Optional[Tuple[int, int]]:
        screenshot = pyautogui.screenshot()
        screenshot_rgb = screenshot.convert("RGB")

        # OpenCV multi-scale matching using pre-cached templates
        if has_cv2 and self._multiscale and self._cached_scaled_templates:
            screenshot_np = cv2.cvtColor(np.array(screenshot_rgb), cv2.COLOR_BGR2GRAY if self._grayscale else cv2.COLOR_BGR2RGB)

            for path, scale, resized_tmpl, sw, sh, min_std, min_max_val in self._cached_scaled_templates:
                if sw >= screenshot_np.shape[1] or sh >= screenshot_np.shape[0]:
                    continue

                res = cv2.matchTemplate(screenshot_np, resized_tmpl, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(res)

                if max_val >= self._confidence:
                    # Check for shaded/dimmed background or disabled button
                    matched_crop = screenshot_np[max_loc[1]:max_loc[1] + sh, max_loc[0]:max_loc[0] + sw]
                    _, std_m = cv2.meanStdDev(matched_crop)
                    max_m = float(matched_crop.max())

                    if std_m[0][0] < min_std or max_m < min_max_val:
                        # Shaded/dimmed in background, ignore!
                        continue

                    match_x = max_loc[0] + sw // 2
                    match_y = max_loc[1] + sh // 2
                    self._log(f"¡Botón detectado! {Path(path).name} (conf: {max_val*100:.1f}%, escala: {scale:.2f}x)")
                    return match_x, match_y
            return None

        # Standard PyAutoGUI matching fallback
        kwargs: Dict[str, Any] = {}
        if has_cv2:
            kwargs["confidence"] = self._confidence

        for path, template_image in self._templates.items():
            box = None
            try:
                box = pyautogui.locate(template_image.convert("RGB"), screenshot_rgb, grayscale=self._grayscale, **kwargs)
            except Exception:
                pass

            if box:
                match_x, match_y = pyautogui.center(box)
                self._log(f"Coincidencia encontrada: {Path(path).name}")
                return match_x, match_y

        return None

    def _loop(self) -> None:
        if not self._running:
            return

        loop_start = time.time()
        sleep_time = 0.11

        try:
            pos = self._match_image()
            if pos:
                self._search_phase = "scan"
                self._phase_start = time.time()
                self._perform_click(pos[0], pos[1])
                min_s, max_s, _ = self._speed_presets[self._selected_speed.get()]
                sleep_time = random.uniform(min_s, max_s)
                self._log(f"Esperando {sleep_time:.1f} segundos para la siguiente descarga...")
            else:
                now = time.time()

                if self._search_phase == "scan":
                    if now - self._phase_start < 0.5:
                        if now - self._last_log_time >= 0.5:
                            self._log("Escaneando pantalla... Esperando botón de descarga.")
                            self._last_log_time = now
                    else:
                        self._search_phase = "scroll_down"
                        self._phase_start = now
                        self._log("Botón no visible. Desplazando hacia abajo (5 segundos)...")

                elif self._search_phase == "scroll_down":
                    elapsed = now - self._phase_start
                    if elapsed < 5.0:
                        pyautogui.scroll(-225)
                        if now - self._last_log_time >= 0.8:
                            remaining = max(0.0, 5.0 - elapsed)
                            self._log(f"Buscando... Desplazando abajo ({remaining:.1f}s restantes)...")
                            self._last_log_time = now
                    else:
                        self._search_phase = "scroll_up"
                        self._phase_start = now
                        self._log("Cambiando dirección: Desplazando hacia arriba (5 segundos)...")

                elif self._search_phase == "scroll_up":
                    elapsed = now - self._phase_start
                    if elapsed < 5.0:
                        pyautogui.scroll(225)
                        if now - self._last_log_time >= 0.8:
                            remaining = max(0.0, 5.0 - elapsed)
                            self._log(f"Buscando... Desplazando arriba ({remaining:.1f}s restantes)...")
                            self._last_log_time = now
                    else:
                        self._log("Botón no encontrado tras 5s abajo y 5s arriba. Recargando página (F5)...", level="click")
                        pyautogui.press("f5")
                        self._search_phase = "scan"
                        self._phase_start = now
                        sleep_time = 3.5

                if sleep_time == 0.11:
                    work_time = time.time() - loop_start
                    sleep_time = max(0.01, 0.11 - work_time)

        except Exception as e:
            self._log(f"Error durante el escaneo: {e}", level="fatal")

        self._timer_id = self._root.after(int(sleep_time * 1000), self._loop)


if __name__ == "__main__":
    root = tk.Tk()
    app = NexusAutoDL(root)
    root.mainloop()
