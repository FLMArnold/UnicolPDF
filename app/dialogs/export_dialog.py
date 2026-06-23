import os
from PyQt6.QtWidgets import QFileDialog, QInputDialog


def show_export_dialog(parent, engine, default_name):
    if not engine.doc:
        return None

    export_dir = QFileDialog.getExistingDirectory(parent, "选择导出路径")
    if not export_dir:
        return None

    project_name, ok = QInputDialog.getText(
        parent, "项目名称", "输入项目名称:", text=default_name
    )
    if not ok or not project_name:
        return None

    save_path = os.path.join(export_dir, f"{project_name}.pdf")
    engine.save(save_path)
    return True
