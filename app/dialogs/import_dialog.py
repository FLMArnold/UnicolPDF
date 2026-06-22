from PyQt6.QtWidgets import QFileDialog


def show_import_dialog(parent):
    pdf_path, _ = QFileDialog.getOpenFileName(
        parent, "选择PDF文件", "", "PDF Files (*.pdf)"
    )
    if not pdf_path:
        return None
    return {"pdf_path": pdf_path}
