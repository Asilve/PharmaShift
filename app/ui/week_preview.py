from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
from PySide6.QtCore import Qt

from ui.day_preview import DayPreview

class WeekPreview(QWidget):

    def __init__(self, days):
        super().__init__()
        self.days = days
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        day_layout = QHBoxLayout()
        day_layout.setContentsMargins(0, 0, 0, 0)
        day_layout.setSpacing(0)

        layout.addLayout(day_layout)

        for day in self.days:
            day_widget = DayPreview(day)
            day_layout.addWidget(day_widget)

        summary = self.create_weekly_summary()
        layout.addWidget(summary)

    def create_weekly_summary(self):
        summary = QFrame()
        summary.setObjectName("weekly_summary")

        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(12, 8, 12, 8)
        summary_layout.setSpacing(20)

        title_label = QLabel("Weekly Total")
        title_label.setStyleSheet("""
            QLabel {
                color: #52636F;
                font-size: 11px;
                font-weight: 600;
            }
        """)

        hours_label = QLabel(self.format_hours(self.total_hours))
        pay_label = QLabel(f"£{self.total_pay:.2f}")

        hours_label.setStyleSheet("""
            QLabel {
                color: #263238;
                font-size: 11px;
                font-weight: 600;
            }
        """)

        pay_label.setStyleSheet("""
            QLabel {
                color: #263238;
                font-size: 11px;
                font-weight: 600;
            }
        """)

        summary_layout.addStretch()
        summary_layout.addWidget(title_label)
        summary_layout.addWidget(hours_label)
        summary_layout.addWidget(pay_label)

        summary.setStyleSheet("""
            #weekly_summary {
                background-color: #F4F7FA;
                border: 1px solid #D7DEE5;
                border-radius: 7px;
            }
        """)

        return summary

    @property
    def total_hours(self):
        return sum(day.total_hours for day in self.days)

    @property
    def total_pay(self):
        return sum(day.total_pay for day in self.days)

    @staticmethod
    def format_hours(hours):
        if hours.is_integer():
            return f"{int(hours)} hours"

        return f"{hours:g} hours"

