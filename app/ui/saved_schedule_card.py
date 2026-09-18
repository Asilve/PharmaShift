from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
from PySide6.QtCore import Qt, Signal

from datetime import datetime


class SavedScheduleCard(QWidget):

    clicked = Signal()

    def __init__(self, saved_schedule):
        super().__init__()

        self.setFixedSize(1180, 100)
        self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)

        loader = QUiLoader()
        self.ui = loader.load("ui_files/schedule_card.ui")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.name_label = self.ui.findChild(QLabel,"name_label")
        self.subtitle_label = self.ui.findChild(QLabel,"date_range_label")
        self.saved_label = self.ui.findChild(QLabel,"last_saved_label")
        self.colour_indicator = self.ui.findChild(QFrame,"colour_indicator")

        self.set_schedule(saved_schedule)

    def set_schedule(self, saved_schedule):
        self.saved_schedule = saved_schedule
        (
            schedule_id,
            employee_name,
            employee_notes,
            employee_colour,
            start_date,
            end_date,
            created_at,
            updated_at
        ) = saved_schedule

        self.name_label.setText(employee_name)

        start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
        updated_at = datetime.strptime(updated_at,"%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")

        self.subtitle_label.setText(f"{start_date} - {end_date}")
        self.saved_label.setText(f"Last saved: {updated_at}")
        self.colour_indicator.setStyleSheet(f"background-color: {employee_colour};")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def set_selected(self, selected):
        self.selected = selected
        self.ui.setProperty("selected","true" if selected else "false")
        stylesheet = self.ui.styleSheet()
        self.ui.setStyleSheet("")
        self.ui.setStyleSheet(stylesheet)