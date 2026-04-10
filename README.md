<div align="center">

# 🖥️ ScreenZen — Screenshot Super-Organizer

**Stop drowning in screenshots. Start finding them instantly.**

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tesseract](https://img.shields.io/badge/Tesseract-OCR-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 📋 Table of Contents

- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Building EXE](#-building-exe)
- [Project Structure](#-project-structure)
- [Future Roadmap](#-future-roadmap)
- [License](#-license)

---

## 😤 The Problem

Your desktop is buried under **1000+ screenshots** and you can never find *"that one image"* when you need it. Filenames like `Screenshot_2026-04-08_123456.png` tell you nothing. Scrolling through folders is a nightmare.

## ✨ The Solution

**ScreenZen** is a lightweight Python desktop app that automatically watches your Windows Screenshots folder, extracts text from new captures using OCR, organizes them by date and tags, and gives you **instant full-text search** across all your images.

> 🔍 Search YOUR screenshots by their **content**, not just filenames.

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| 👁️ **Auto Screenshot Detection** | Watches your Screenshots folder in the background — no manual import needed |
| 🔤 **OCR Text Extraction** | Powered by Tesseract — extracts all visible text from images automatically |
| ✅ **Confirm Dialog** | Review, rename, and verify metadata before a screenshot is saved |
| 🏷️ **Smart Tagging** | Auto-generated keyword tags from OCR results |
| 📅 **Date Grouping** | Screenshots organized by capture/import date |
| 🔍 **Full-Text Search** | Search across ALL extracted text instantly |
| 🖼️ **Gallery View** | Grid gallery with image previews and image cards |
| 📂 **Drag & Drop Upload** | Also supports manual import via file dialog or drag-and-drop zone |
| 💾 **Local SQLite DB** | All data stored locally — no cloud, no privacy concerns |
| 🌙 **Dark Theme** | Modern, eye-friendly dark UI built with CustomTkinter |
| 🔔 **System Tray** | Runs quietly in the background via system tray icon (pystray) |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.9+ |
| **GUI Framework** | CustomTkinter (modern tkinter wrapper) |
| **OCR Engine** | Tesseract OCR via `pytesseract` |
| **Image Processing** | Pillow (PIL) |
| **Database** | SQLite3 (built-in) |
| **Folder Watcher** | `watchdog` — monitors Screenshots folder for new files |
| **System Tray** | `pystray` — background tray icon |
| **Packaging** | PyInstaller (for `.exe` conversion) |

---

## 📦 Installation

### Prerequisites

1. **Python 3.9+** — [Download here](https://www.python.org/downloads/)
2. **Tesseract OCR** — [Download here](https://github.com/UB-Mannheim/tesseract/wiki)
   - During installation, note the install path (default: `C:\Program Files\Tesseract-OCR`)
   - Add Tesseract to your system PATH, or the app will auto-detect common paths

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/screenzen.git
cd screenzen

# 2. Create a virtual environment (recommended)
python -m venv venv

# 3. Activate the virtual environment
# Windows:
venv\Scripts\activate
# Windows (Git Bash / Bash):
source venv/Scripts/activate
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

### Running the App

```bash
python main.py
```

---

## 🎯 Usage

### Option A — Run with the batch script (easiest)

Double-click `run.bat`. It activates the virtual environment and launches the app automatically.

### Option B — Run manually from terminal

```bash
venv\Scripts\activate
python main.py
```

### Workflow

1. **Launch** the app — it starts monitoring your Screenshots folder in the background
2. **Take a screenshot** — Windows `Win + PrtScn`, Snipping Tool, or Snip & Sketch
3. **Confirm** — a dialog appears asking you to review the OCR-extracted text and save
4. **Browse** — use the gallery view to browse, filter by date or tags
5. **Search** — type any keyword in the search bar to find matching screenshots instantly

> The background watcher monitors these folders automatically:
> - `~/Pictures/Screenshots`
> - `~/OneDrive/Pictures/Screenshots`
> - `~/Videos/Captures` (Snip & Sketch)

---

## 🏗️ Building EXE

### Option A — Use the batch script

Double-click `build_exe.bat`. It cleans previous builds, checks for PyInstaller, and produces `dist\ScreenZen.exe`.

### Option B — Manual PyInstaller command

```bash
# Activate venv first
venv\Scripts\activate

# Build (with icon)
pyinstaller --onefile --windowed --name ScreenZen --icon=assets\icon.ico main.py

# Output: dist\ScreenZen.exe
```

> **Note:** Tesseract OCR must be separately installed on the target machine. To bundle Tesseract inside the EXE:
>
> ```bash
> pyinstaller --onefile --windowed --name ScreenZen --icon=assets\icon.ico ^
>   --add-data "C:\Program Files\Tesseract-OCR;Tesseract-OCR" ^
>   main.py
> ```

---

## 📁 Project Structure

```
screenzen/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── setup.bat                    # One-click setup script
├── run.bat                      # One-click launcher
├── build_exe.bat                # One-click EXE builder
├── ScreenZen.spec               # PyInstaller spec file
├── README.md                    # This file
├── LICENSE
├── assets/
│   └── icon.ico                 # App icon
├── screenzen/                   # Core Python package
│   ├── __init__.py
│   ├── app.py                   # Main application window
│   ├── database.py              # SQLite database manager
│   ├── ocr_engine.py            # Tesseract OCR wrapper
│   ├── image_manager.py         # Image import / processing / export
│   ├── search_engine.py         # Full-text search logic
│   ├── background_monitor.py    # Watchdog-based Screenshots folder watcher
│   └── widgets/
│       ├── confirm_dialog.py    # OCR review & confirm dialog
│       ├── drop_zone.py         # Drag & drop upload zone
│       ├── gallery.py           # Gallery grid view widget
│       ├── image_card.py        # Individual image card widget
│       └── search_bar.py        # Search bar widget
├── data/                        # Runtime data (auto-created)
│   ├── screenzen.db             # SQLite database
│   ├── images/                  # Saved screenshot copies
│   └── thumbnails/              # Cached image thumbnails
└── tests/
    └── test_ocr.py              # Basic OCR tests
```

---

## 🗺️ Future Roadmap

- [ ] **Annotation Tools** — Draw, highlight, and annotate screenshots
- [ ] **Cloud Sync** — Optional cloud storage with team sharing
- [ ] **AI Tagging** — Smart categorization using ML models
- [ ] **Multi-language OCR** — Support for non-English text extraction
- [ ] **Batch Operations** — Bulk tag, delete, or export
- [ ] **Keyboard Shortcuts** — Power-user productivity features
- [ ] **Export ZIP** — Select and export screenshots as a zip archive

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for the hackathon**

*Stop scrolling. Start searching.*

</div>
