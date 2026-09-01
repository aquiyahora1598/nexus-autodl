# Nexus AutoDL - Wabbajack & Nexus Autoclicker

<p align="center">
  <img alt="Nexus AutoDL" src="https://raw.githubusercontent.com/parsiad/nexus-autodl/master/assets/img/logo.png">
</p>

When downloading mods using **Wabbajack** or from **Nexus Mods**, non-premium users are required to manually click the **"Slow download"** button every time a new mod is added to the download queue.
For large modlists containing hundreds or thousands of mods, clicking this button repeatedly is extremely tedious.

**Nexus AutoDL** automates this process for you using intelligent OpenCV multi-scale image recognition.

---

## Key Features

- 🖼️ **Automated Image Recognition (OpenCV & PyAutoGUI)**: Automatically detects the "Slow download" button anywhere on your screen using template matching with confidence thresholding.
- ⚡ **3 Preset Speed Modes**:
  - 🚀 **Rápido (Fast)**: Randomized interval of 8 to 11 seconds.
  - ⚡ **Normal (Recommended)**: Randomized interval of 15 to 21 seconds.
  - 🛡️ **Lento (Safe / Slow)**: Randomized interval of 43 to 56 seconds.
- 📦 **Pre-Bundled Factory Templates**: Comes out-of-the-box with updated default templates (`Slow download.png` and `Standard download.png`) embedded directly inside the application.
- 📂 **Easy Custom Templates**: Click **"📂 Abrir Carpeta de Plantillas"** to view, add, or customize your own screenshot templates anytime.
- 📐 **High-DPI & Multi-Scale Support**: Windows DPI-aware (`SetProcessDpiAwareness`) with multi-scale OpenCV template matching so button detection works across different zoom levels and screen resolutions.
- 🔄 **Smart Navigation & Auto-Recovery (Wabbajack Fix)**: If the download button is not immediately visible on screen, Nexus AutoDL smoothly scrolls down for 5 seconds and up for 5 seconds to locate it. If still not found, it automatically presses `F5` to refresh the page and resume unattended downloading.
- 🖱️ **Mouse Return**: Automatically restores your mouse cursor back to its previous position after clicking, allowing you to use your PC without cursor disruption.
- 🖥️ **Modern Single-Window UI**: Clean dark theme with status indicators, speed selection buttons, and a live console log.

---

## How to Use with Wabbajack

1. Download and launch **Nexus AutoDL**.
2. Select your preferred speed (**Rápido**, **Normal**, or **Lento**).
3. Open **Wabbajack** and start downloading your modlist.
4. Click **▶ INICIAR AUTOCLICKER**.
5. Sit back and watch Nexus AutoDL handle the manual download clicks automatically!

---

## Download & Build

### Binary Releases
Pre-compiled standalone Windows executables are available on the [Releases page](https://github.com/aquiyahora1598/nexus-autodl/releases/).

### Running from Source
```bash
pip install -r requirements.txt
python nexus_autodl.py
```

### Compiling to Executable (.exe)
```bash
pip install pyinstaller
make build
```
The compiled executable will be generated inside `dist/nexus_autodl.exe`.

---

## Credits & Acknowledgments

This project is an updated and modernized fork based on the original open-source work by [Parsiad Azimzadeh](https://github.com/parsiad) and [Ellen Arteca](https://github.com/arteca):
- Original Repository: [parsiad/nexus-autodl](https://github.com/parsiad/nexus-autodl)
- License: MIT

---

## Caution

Using automation tools on Nexus Mods may violate their TOS:
> Attempting to download files or otherwise record data offered through our services in a fashion that drastically exceeds the expected average, through the use of software automation or otherwise, is prohibited without expressed permission.

Use at your own risk.
