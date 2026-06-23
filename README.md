# UnicolPDF

A PDF batch processing editor with dark theme, supporting page operations with undo/redo history and crash recovery.

## Features

- **PDF Import/Export** — Open any PDF, save as new file with page operations applied
- **Page Operations** — Insert pages before/after current page, delete pages
- **Batch Processing** — Apply operations to all non-excluded pages at once (toggle via checkbox or hold Space key)
- **Per-Page Exclusion** — Mark individual pages to skip during batch operations
- **History & Undo/Redo** — Full operation history with timeline view; Ctrl+Z to undo, Ctrl+Y to redo
- **Auto-Save & Crash Recovery** — Auto-saves at configurable intervals; recovers unsaved work on restart
- **Background Settings** — Set background image with fill/crop/stretch/dense modes; persists across sessions
- **Page Settings** — Adjust DPI and page aspect ratio with no-loss pixel algorithm
- **Customizable Shortcuts** — Configure key bindings for all three operations
- **Dark Theme** — Built-in dark color scheme

## Requirements

- Python 3.10+
- PyQt6
- PyMuPDF
- Pillow

## Quick Start

```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

## Project Structure

```
UnicolPDF/
├── app/                    # Application package
│   ├── dialogs/            # Dialog windows (import, export, settings)
│   ├── main_window.py      # Main window with layout and batch logic
│   ├── pdf_engine.py       # Core PDF operations and rendering
│   ├── viewer_widget.py    # PDF page display widget
│   ├── operation_widget.py # Page operation buttons
│   ├── page_info_panel.py  # Page info and per-page anti-batch control
│   ├── batch_panel.py      # Batch mode toggle
│   ├── history_manager.py  # Undo/redo history with in-memory snapshots
│   ├── history_panel.py    # History timeline tab widget
│   ├── tool_panel.py       # Tool sidebar placeholder
│   └── menu_bar.py         # Application menu
├── resources/              # Static assets
│   └── styles.qss          # Dark theme stylesheet
├── docs/                   # Design documents and specs
├── main.py                 # Entry point
└── requirements.txt        # Python dependencies
```

## Keyboard Shortcuts

| Operation | Default |
|-----------|---------|
| Import PDF | Ctrl+O |
| Export PDF | Ctrl+S |
| Undo | Ctrl+Z |
| Redo | Ctrl+Y |
| Exit | Ctrl+Q |
| Batch Mode (hold) | Space |

Page operations and their shortcuts can be customized via **设置 → 快捷键**.
