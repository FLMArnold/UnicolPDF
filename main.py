import sys
import os
from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow


def load_styles(app):
    qss_path = os.path.join(os.path.dirname(__file__), "resources", "styles.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Unicol PDF")
    load_styles(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
