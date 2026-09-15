from PySide6.QtCore import Signal, QDate
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCalendarWidget, QLabel
from PySide6.QtUiTools import QUiLoader


class SelectDatePage(QWidget):

    back_clicked = Signal()
    continue_clicked = Signal(object, object)

    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.ui = loader.load("ui_files/select_date.ui", None)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # Buttons
        self.back_button = self.ui.findChild(QPushButton,"back_button")
        self.continue_button = self.ui.findChild(QPushButton,"continue_button")

        # Calendars
        self.start_calendar = self.ui.findChild(QCalendarWidget,"start_calendar")
        self.end_calendar = self.ui.findChild(QCalendarWidget,"end_calendar")

        # Date information
        self.date_range_label = self.ui.findChild(QLabel,"date_range_label")
        self.days_label = self.ui.findChild(QLabel,"days_label")

        # Selected dates
        self.start_date = None
        self.end_date = None

        # Connections
        self.back_button.clicked.connect(self.back_clicked.emit)
        self.continue_button.clicked.connect(self.continue_to_holidays)
        self.start_calendar.clicked.connect(self.select_start_date)
        self.end_calendar.clicked.connect(self.select_end_date)

        # Initial state
        self.continue_button.setEnabled(False)

        self.update_date_display()

    def select_start_date(self, date):
        self.start_date = date

        # If the new start date is after the current end date,
        # move the end date to match it.
        if self.end_date is not None and date > self.end_date:
            self.end_date = date
            self.end_calendar.setSelectedDate(date)

        # Prevent the end calendar from selecting anything
        # before the new start date.
        self.end_calendar.setMinimumDate(date)

        self.update_date_display()

    def select_end_date(self, date):
        self.end_date = date
        self.update_date_display()

    def update_date_display(self):
        if self.start_date is None or self.end_date is None:
            self.date_range_label.setText(
                "Select a start and end date"
            )
            self.days_label.setText(
                "0 days"
            )
            self.continue_button.setEnabled(False)
            return

        days = self.start_date.daysTo(self.end_date) + 1

        self.date_range_label.setText(
            f"{self.start_date.toString('d MMMM yyyy')} "
            f" - "
            f"{self.end_date.toString('d MMMM yyyy')}"
        )

        self.days_label.setText(
            f"{days} days"
        )

        self.continue_button.setEnabled(
            self.start_date <= self.end_date
        )

    def continue_to_holidays(self):
        if self.start_date is None or self.end_date is None:
            return

        if self.start_date > self.end_date:
            return

        self.continue_clicked.emit(
            self.start_date,
            self.end_date
        )