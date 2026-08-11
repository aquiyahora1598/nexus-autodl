# Nexus AutoDL - Wabbajack & Nexus Autoclicker

<p align="center">
  <img alt="Nexus AutoDL" src="https://raw.githubusercontent.com/parsiad/nexus-autodl/master/assets/img/logo.png">
</p>

When downloading mods using **Wabbajack** or from **Nexus Mods**, non-premium users are required to manually click the **"Slow download"** button every time a new mod is added to the download queue.
For large modlists containing hundreds or thousands of mods, clicking this button repeatedly is extremely tedious.

**Nexus AutoDL** automates this process for you.

---

## Key Features

- 🎯 **Fixed Screen Position Mode (Recommended for Wabbajack)**: Set an exact $(X, Y)$ screen coordinate or use the **"Pick Position"** 3-second hover countdown to target the Wabbajack button. Auto-clicks that exact location on a customizable schedule.
- 🖼️ **Image Matching Mode (OpenCV & PyAutoGUI)**: Automatically detects the "Slow download" button anywhere on screen using bundled high-res template images.
- 📐 **High-DPI & Multi-Scale Support**: Windows DPI-aware (`SetProcessDpiAwareness`) so clicks land accurately on 100%, 125%, 150%, and 200% scaled displays, with multi-scale OpenCV template matching.
- 🖱️ **Mouse Return**: Automatically restores your mouse cursor back to where you were working immediately after performing a click.
- ⏱️ **Randomized Click Interval**: Custom min/max sleep intervals (e.g. 1.5 to 4.0s) to simulate human clicking and prevent rapid spam.
- 🖥️ **Integrated Live Console & Status**: Single-window modern dark UI with real-time logging, status badges, and template management.

---

## How to Use with Wabbajack

1. Download and launch **Nexus AutoDL**.
2. Open **Wabbajack** and start downloading your modlist.
3. When Wabbajack opens the embedded Nexus manual download window:
   - **Method A (Fixed Position)**: Select *Fixed Screen Position*, click **🎯 Pick Position (3s)**, hover your cursor over the **Slow download** button, and wait 3 seconds for coordinates to capture.
   - **Method B (Image Matching)**: Select *Image Matching* mode to automatically search your screen for the button using pre-bundled templates in `templates/`.
4. Click **▶ START AUTOCLICKER**.
5. Sit back and watch Nexus AutoDL handle the manual download clicks automatically!

---

## Download & Build

### Binary Releases
Pre-compiled Windows executables are available on the [Releases page](https://github.com/parsiad/nexus-autodl/releases).

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
Executable will be placed inside `dist/nexus_autodl.exe`.

---

## Caution

Using automation tools on Nexus Mods may violate their TOS:
> Attempting to download files or otherwise record data offered through our services in a fashion that drastically exceeds the expected average, through the use of software automation or otherwise, is prohibited without expressed permission.

Use at your own risk.

