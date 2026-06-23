from PyQt6.QtGui import QAction, QKeySequence


def build_menu(main_window):
    menubar = main_window.menuBar()

    file_menu = menubar.addMenu("文件")

    import_action = QAction("导入", main_window)
    import_action.setShortcut(QKeySequence("Ctrl+O"))
    import_action.triggered.connect(lambda: main_window.on_import())
    file_menu.addAction(import_action)

    export_action = QAction("导出", main_window)
    export_action.setShortcut(QKeySequence("Ctrl+S"))
    export_action.triggered.connect(lambda: main_window.on_export())
    file_menu.addAction(export_action)

    file_menu.addSeparator()

    exit_action = QAction("退出", main_window)
    exit_action.setShortcut(QKeySequence("Ctrl+Q"))
    exit_action.triggered.connect(main_window.close)
    file_menu.addAction(exit_action)

    image_menu = menubar.addMenu("图像")

    page_settings_action = QAction("页面设置", main_window)
    page_settings_action.triggered.connect(lambda: main_window.on_page_settings())
    image_menu.addAction(page_settings_action)

    bg_action = QAction("自定义背景", main_window)
    bg_action.triggered.connect(lambda: main_window.on_background_settings())
    image_menu.addAction(bg_action)

    settings_menu = menubar.addMenu("设置")

    shortcut_action = QAction("快捷键", main_window)
    shortcut_action.triggered.connect(lambda: main_window.on_shortcut_settings())
    settings_menu.addAction(shortcut_action)

    settings_menu.addSeparator()

    history_limit_action = QAction("历史操作上限", main_window)
    history_limit_action.triggered.connect(lambda: main_window.on_history_limit_settings())
    settings_menu.addAction(history_limit_action)

    autosave_action = QAction("自动保存设置", main_window)
    autosave_action.triggered.connect(lambda: main_window.on_autosave_settings())
    settings_menu.addAction(autosave_action)

    return menubar
