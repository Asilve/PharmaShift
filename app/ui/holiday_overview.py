from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtUiTools import QUiLoader


class HolidayOverviewPage(QWidget):

    back_clicked = Signal()

    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.ui = loader.load("ui_files/holiday_overview.ui", None)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.back_button = self.ui.findChild(QPushButton,"back_button")

        self.back_button.clicked.connect(self.back_clicked.emit)