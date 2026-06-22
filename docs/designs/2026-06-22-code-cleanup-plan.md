# Code Cleanup Implementation Plan

> **For agentic workers:** Inline execution — all tasks are trivial deletions/edits.

**Goal:** Clean up all unused imports, dead code, style issues, and add `.gitignore`

**Architecture:** Direct file edits only — no behavioral changes, no new features

**Tech Stack:** Python 3.13.5, PyQt6

## Global Constraints

- No behavioral changes — deletions and extractions only
- Syntax must remain valid after each edit (verified with `ast.parse`)
- All changes must be in `D:\Codes\PDFeditor`

---

### Task 1: Unused Imports

**Files:** Modify `app/menu_bar.py`, `app/pdf_engine.py`, `app/dialogs/import_dialog.py`

- [ ] Remove `from PyQt6.QtWidgets import QMenuBar` from `menu_bar.py`
- [ ] Remove `from PyQt6.QtCore import Qt` from `pdf_engine.py` (keep `QRect`)
- [ ] Remove `import os` from `import_dialog.py`
- [ ] Syntax check all three files

### Task 2: Dead Code

**Files:** Modify `app/pdf_engine.py`, `app/page_info_panel.py`, `app/batch_panel.py`

- [ ] Delete method `set_bg_color` from `pdf_engine.py`
- [ ] Delete method `is_anti_batch` from `page_info_panel.py`
- [ ] Delete method `is_batch_mode` from `batch_panel.py`

### Task 3: Dead Parameter + Call Site

**Files:** Modify `app/menu_bar.py`, `app/main_window.py`

- [ ] Change `build_menu(main_window, engine)` to `build_menu(main_window)` in `menu_bar.py`
- [ ] Update call site `build_menu(self, self.engine)` to `build_menu(self)` in `main_window.py:86`

### Task 4: Hoist Local Import

**Files:** Modify `app/dialogs/page_settings_dlg.py`

- [ ] Add `from app.pdf_engine import PDFEngine` at module top
- [ ] Remove lines 127 and 139 local imports

### Task 5: Remove Unused Result Key

**Files:** Modify `app/dialogs/page_settings_dlg.py`

- [ ] Remove `"unit": self.unit_combo.currentText()` from `get_result()` dict

### Task 6: Deduplicate Key Capture

**Files:** Modify `app/dialogs/shortcut_dlg.py`

- [ ] Extract `_capture_key(self, event)` helper from repeated logic
- [ ] Call it from both `eventFilter` and `keyPressEvent`

### Task 7: Fix test_mode.py

**Files:** Modify `test_mode.py`

- [ ] Replace hardcoded path with computed path
- [ ] Remove semicolons

### Task 8: Infrastructure

- [ ] Create `.gitignore`
- [ ] Delete `__pycache__` directories
- [ ] Run final syntax check on all files
