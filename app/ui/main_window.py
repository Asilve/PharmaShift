from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QStackedWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pharma Shift")
        self.setFixedSize(1280,720)

        loader = QUiLoader()
        main_ui = loader.load("ui_files/main_window.ui")
        home_ui = loader.load("ui_files/home.ui")

        self.setCentralWidget(main_ui)

        page_stack = main_ui.findChild(QStackedWidget, "page_stack")
        page_stack.addWidget(home_ui)
        page_stack.setCurrentWidget(home_ui)
