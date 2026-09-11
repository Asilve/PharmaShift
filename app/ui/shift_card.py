from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Signal, Qt

from models.shift import Shift

class ShiftCard(QWidget):

    clicked = Signal(object)

    def __init__(self, shift: Shift):
        super().__init__()

        self.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Minimum
        )
        self.setMinimumHeight(60)

        loader = QUiLoader()
        self.ui = loader.load("ui_files/shift_card.ui")

        self.ui.setObjectName("shift_card")

        # Find the actual content widget inside the .ui
        self.layout_widget = self.ui.findChild(
            QWidget,
            "verticalLayoutWidget"
        )

        # Give the loaded root widget a real layout
        self.ui_layout = QVBoxLayout(self.ui)
        self.ui_layout.setContentsMargins(0, 0, 0, 0)
        self.ui_layout.addWidget(self.layout_widget)

        # Put the loaded UI inside ShiftCard
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # Find controls
        self.name_label = self.ui.findChild(QLabel, "name_label")
        self.hours_label = self.ui.findChild(QLabel, "hours_label")
        self.start_label = self.ui.findChild(QLabel, "start_label")
        self.end_label = self.ui.findChild(QLabel, "end_label")
        self.time_container = self.ui.findChild(
            QWidget,
            "time_container_2"
        )

        self.set_shift(shift)
        

    def set_shift(self, shift):
        self.shift = shift

        if shift.hours.is_integer():
            hours_text = f"{int(shift.hours)} hours"
        else:
            hours_text = f"{shift.hours:g} hours"

        self.name_label.setText(shift.location)
        self.hours_label.setText(hours_text)

        if shift.start_time is None and shift.end_time is None:
            self.time_container.hide()
            self.hours_label.setAlignment(Qt.AlignHCenter)
        else:
            self.start_label.setText(shift.start_time)
            self.end_label.setText(shift.end_time)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.shift)

