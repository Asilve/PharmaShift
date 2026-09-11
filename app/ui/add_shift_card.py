from PySide6.QtCore import Signal, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout


class AddShiftCard(QWidget):

    clicked = Signal()

    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.ui = loader.load("ui_files/add_shift_card.ui", None)

        # Put the loaded UI inside this widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()