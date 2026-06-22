# Code Cleanup Design

## Scope

Audit-driven cleanup of all Python files in the UnicolPDF project. Operations only:
no behavioral changes, no new features, no refactoring beyond removing dead code.

## Items

### 1. Remove Unused Imports
- `app/menu_bar.py:2` — remove `from PyQt6.QtWidgets import QMenuBar`
- `app/pdf_engine.py:4` — remove `from PyQt6.QtCore import Qt` (keep `QRect`)
- `app/dialogs/import_dialog.py:1` — remove `import os`

### 2. Remove Dead Code
- `app/pdf_engine.py` — delete method `set_bg_color(self, color)`
- `app/page_info_panel.py` — delete method `is_anti_batch(self)`
- `app/batch_panel.py` — delete method `is_batch_mode(self)`

### 3. Remove Dead Parameter
- `app/menu_bar.py` — `build_menu(main_window, engine)` -> `build_menu(main_window)`
- `app/main_window.py:86` — update call site

### 4. Hoist Local Imports
- `app/dialogs/page_settings_dlg.py` — move `from app.pdf_engine import PDFEngine`
  from lines 127/139 to module top

### 5. Remove Unused Result Key
- `app/dialogs/page_settings_dlg.py` — remove `"unit"` from `get_result()` dict

### 6. Deduplicate Key Capture Logic
- `app/dialogs/shortcut_dlg.py` — extract shared `_capture_key(event)` helper
  from `eventFilter` and `keyPressEvent`

### 7. Fix test_mode.py
- Replace hardcoded `'D:/Codes/PDFeditor'` with computed path
- Remove semicolons (multi-statement lines)

### 8. Project Infrastructure
- Add `.gitignore` (python standard + `__pycache__`, `.venv`, `.DS_Store`)
- Delete all `__pycache__` directories

### 9. Update AGENTS.md
- Record this cleanup session in progress notes

## Risk Assessment
- All changes are deletions or extractions — zero risk of behavioral regression
- Confirmed with `py_compile` and `ast.parse` that syntax is valid before/after
