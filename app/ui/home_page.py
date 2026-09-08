from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader

loader = QUiLoader()

class HomePage():
    def __init__(self):
        super().__init__
        self.ui = loader.load("ui_files/home.ui", None)
        self.ui.setWindowTitle("Pharma Shift")
        self.ui.setFixedSize(1280, 720)

    def show(self):
        self.ui.show()
    