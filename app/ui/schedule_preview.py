from PySide6.QtCore import Qt, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLayout, QFrame, QHBoxLayout, QLabel

from ui.week_preview import WeekPreview
from ui.schedule_header import ScheduleHeader
from ui.preview_page import PreviewPage


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

        # Centre the A4 page horizontally
        self.preview_content_layout.setAlignment(Qt.AlignHCenter)

        # Preview Page
        self.preview_page = PreviewPage()
        self.preview_content_layout.addWidget(self.preview_page)

        # Scrolling
        self.preview_content.setMinimumHeight(767)

        # Connect signals
        self.back_button.clicked.connect(self.back_clicked.emit)


    def set_schedule(self, schedule):
        self.schedule = schedule

    def show_first_week(self):
        if self.schedule is None:
            return

        page_layout = self.preview_page.page_layout
        header = ScheduleHeader(self.schedule)
        page_layout.addWidget(header)

        for i in range(0, len(self.schedule.days), 7):
            week_days = self.schedule.days[i:i + 7]
            week_widget = WeekPreview(week_days, self.schedule.start_date, self.schedule.end_date)
            page_layout.addWidget(week_widget)

        period_summary = self.create_period_summary()
        page_layout.addWidget(period_summary)


    def create_period_summary(self):
        summary = QFrame()
        summary.setObjectName("period_summary")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(12, 10, 12, 10)
        summary_layout.setSpacing(20)

        title_label = QLabel("Period Total")

        title_label.setStyleSheet("""
            QLabel {
                color: #52636F;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        hours_label = QLabel(self.format_hours(self.schedule.total_hours))
        pay_label = QLabel(f"£{self.schedule.total_pay:.2f}")

        hours_label.setStyleSheet("""
            QLabel {
                color: #263238;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        pay_label.setStyleSheet("""
            QLabel {
                color: #263238;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        summary_layout.addStretch()
        summary_layout.addWidget(title_label)
        summary_layout.addWidget(hours_label)
        summary_layout.addWidget(pay_label)

        summary.setStyleSheet("""
            #period_summary {
                background-color: #E9EEF1;
                border: 1px solid #C7D0D6;
                border-radius: 7px;
            }
        """)

        return summary

    @staticmethod
    def format_hours(hours):
        if hours.is_integer():
            return f"{int(hours)} hours"

        return f"{hours:g} hours"