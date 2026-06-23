## GitHub 仓库

项目地址：https://github.com/FLMArnold/UnicolPDF

每次 git 前先看 README 还能不能驾驭得了更新内容。如果驾驭不了了，把 README 也更新。

## 绝对禁止

不能修改/删除/上传人工编写的需求文档（SPECv0.1.txt、SPECv0.2.txt、SPECv0.3.txt 等）。这些文件仅本地留存，不应出现在远程仓库中。

## Python 虚拟环境

运行所有 Python 文件前，先激活虚拟环境：

```powershell
.venv\Scripts\Activate.ps1
```

或者在命令中直接指定 Python 解释器路径：

```powershell
.venv\Scripts\python.exe <script>.py
```

## 项目整理记录 (2026-06-22)

### 清理
- `menu_bar.py`：移除未用 import `QMenuBar`
- `pdf_engine.py`：移除未用 import `Qt` + 死方法 `set_bg_color`
- `import_dialog.py`：移除未用 import `os`
- `page_info_panel.py`：移除死方法 `is_anti_batch`
- `batch_panel.py`：移除死方法 `is_batch_mode`
- `menu_bar.py`：移除 `build_menu` 死参数 `engine`
- `page_settings_dlg.py`：局部 import 提升到文件顶部；移除 `get_result()` 中未用 key `"unit"`
- `shortcut_dlg.py`：抽离 `_capture_key(event)` 去重 eventFilter/keyPressEvent
- `test_mode.py`：修复硬编码路径 + 分号问题
- 添加 `.gitignore`；删除所有 `__pycache__`
- 全部通过 syntax check 和 import 验证
