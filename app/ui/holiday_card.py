from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QFrame, QLabel, QPushButton, QVBoxLayout, QSizePolicy
from PySide6.QtUiTools import QUiLoader


class HolidayCard(QWidget):

    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, holiday, employee_name, employee_colour, parent=None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Minimum)
        self.setMinimumHeight(80)

        self.holiday = holiday
        self.employee_name = employee_name
        self.employee_colour = employee_colour

        self.load_ui()
        self.setup_ui()
        self.update_display()
        self.connect_signals()

    def load_ui(self):
        loader = QUiLoader()
        self.ui = loader.load("ui_files/holiday_card.ui")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.ui)
        self.employee_colour_frame = self.ui.findChild(QFrame,"employee_colour")
        self.employee_label = self.ui.findChild(QLabel,"employee_label")
        self.date_label = self.ui.findChild(QLabel,"date_label")
        self.details_label = self.ui.findChild(QLabel,"details_label")
        self.edit_button = self.ui.findChild(QPushButton,"edit_button")
        self.delete_button = self.ui.findChild(QPushButton,"delete_button")

    def setup_ui(self):
        self.employee_colour_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.employee_colour};
                border-radius: 3px;
            }}
            """
        )

    def connect_signals(self):
        self.edit_button.clicked.connect(self.request_edit)
        self.delete_button.clicked.connect(self.request_delete)

    def request_edit(self):
        self.edit_requested.emit(self.holiday.id)

    def request_delete(self):
        self.delete_requested.emit(self.holiday.id)

    def update_display(self):
        self.employee_label.setText(self.employee_name)

        # Date
        if self.holiday.start_date == self.holiday.end_date:
            date_text = self.holiday.start_date.toString("d MMMM yyyy")
        else:
            date_text = (
                f"{self.holiday.start_date.toString('d MMMM yyyy')}"
                f" - "
                f"{self.holiday.end_date.toString('d MMMM yyyy')}"
            )

        self.date_label.setText(date_text)


        # Details
        if self.holiday.start_date != self.holiday.end_date:
            details_text = "Holiday period · Full day"
        elif (self.holiday.start_time is not None and self.holiday.end_time is not None):
            details_text = (
                f"Part of day · "
                f"{self.holiday.start_time} - "
                f"{self.holiday.end_time}"
            )

        else:
            details_text = "Full day"
        self.details_label.setText(details_text)
