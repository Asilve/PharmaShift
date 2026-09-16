from PySide6.QtCore import Qt, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLayout

from ui.week_preview import WeekPreview
from ui.schedule_header import ScheduleHeader


class SchedulePreviewPage(QWidget):

    back_clicked = Signal()

    def __init__(self):
        super().__init__()

        self.schedule = None

        loader = QUiLoader()
        self.ui = loader.load("ui_files/schedule_preview.ui", None)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # Find widgets from Designer
        self.back_button = self.ui.findChild(QPushButton,"back_button")
        self.preview_content_layout = self.ui.findChild(QLayout,"preview_layout")
        self.preview_content = self.ui.findChild(QWidget,"preview_content")
        self.page_layout = self.ui.findChild(QLayout,"page_layout")

        # Centre the A4 page horizontally
        self.preview_content_layout.setAlignment(Qt.AlignHCenter)

        # Scrolling
        self.preview_content.setMinimumHeight(767)

        # Connect signals
        self.back_button.clicked.connect(self.back_clicked.emit)


    def set_schedule(self, schedule):
        self.schedule = schedule

    def show_first_week(self):
        if self.schedule is None:
            return

        header = ScheduleHeader(self.schedule)
        first_week = self.schedule.days[:7]
        week_widget = WeekPreview(first_week)
        self.page_layout.addWidget(header)
        self.page_layout.addWidget(week_widget)