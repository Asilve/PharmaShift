from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtUiTools import QUiLoader


class SelectDatePage(QWidget):

    back_clicked = Signal()
    continue_clicked = Signal()

    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.ui = loader.load("ui_files/select_date.ui", None)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.back_button = self.ui.findChild(QPushButton,"back_button")
        self.continue_button = self.ui.findChild(QPushButton, "continue_button")

        self.back_button.clicked.connect(self.back_clicked.emit)
        self.continue_button.clicked.connect(self.continue_clicked.emit)