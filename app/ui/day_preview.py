from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget,QVBoxLayout,QLabel,QFrame,QSizePolicy

from ui.shift_preview import ShiftPreview

class DayPreview(QWidget):

    def __init__(self, day, start_date, end_date):
        super().__init__()
        self.day = day
        self.start_date = start_date
        self.end_date = end_date
        self.in_period = (self.start_date <= self.day.date <= self.end_date)

        self.setup_ui()

    def setup_ui(self):
        if not self.in_period:
            self.create_outside_period_ui()
            return

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(42)

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(2, 2, 2, 2)
        header_layout.setSpacing(2)

        day_label = QLabel(self.day.date.toString("ddd").upper())
        date_label = QLabel(self.day.date.toString("d MMM"))

        day_label.setAlignment(Qt.AlignCenter)
        date_label.setAlignment(Qt.AlignCenter)

        day_label.setStyleSheet("""
            QLabel {
                color: #52636F;
                font-size: 10px;
                font-weight: 600;
            }
        """)

        date_label.setStyleSheet("""
            QLabel {
                color: #263238;
                font-size: 14px;
                font-weight: 600;
            }
        """)

        header_layout.addWidget(day_label)
        header_layout.addWidget(date_label)

        shift_area = QFrame()
        shift_area.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        shift_layout = QVBoxLayout(shift_area)
        shift_layout.setContentsMargins(6, 6, 6, 6)
        shift_layout.setSpacing(6)
        shift_layout.setAlignment(Qt.AlignTop)

        for shift in self.day.shifts:
            shift_widget = ShiftPreview(shift)
            shift_layout.addWidget(shift_widget)

        summary = QFrame()
        summary.setObjectName("day_summary")
        summary.setFixedHeight(50)

        summary_layout = QVBoxLayout(summary)
        summary_layout.setContentsMargins(6, 4, 6, 4)
        summary_layout.setSpacing(1)

        if self.day.shifts:
            hours_label = QLabel(self.format_hours(self.day.total_hours))
            pay_label = QLabel(f"£{self.day.total_pay:.2f}")

            hours_label.setAlignment(Qt.AlignCenter)
            pay_label.setAlignment(Qt.AlignCenter)

            hours_label.setStyleSheet("""
                QLabel {
                    color: #263238;
                    font-size: 11px;
                    font-weight: 600;
                }
            """)

            pay_label.setStyleSheet("""
                QLabel {
                    color: #71808A;
                    font-size: 10px;
                }
            """)

            summary_layout.addWidget(hours_label)
            summary_layout.addWidget(pay_label)

        else:
            summary_label = QLabel("---")
            summary_label.setAlignment(Qt.AlignCenter)

            summary_label.setStyleSheet("""
                QLabel {
                    color: #9AA4AB;
                    font-size: 10px;
                }
            """)

            summary_layout.addWidget(summary_label)

        layout.addWidget(header)
        layout.addWidget(shift_area, 1)
        layout.addWidget(summary)

        header.setObjectName("day_header")
        shift_area.setObjectName("shift_area")
        summary.setObjectName("day_summary")

        self.setStyleSheet("""
            #day_header {
                background-color: white;
                border: 1px solid #D7DEE5;
            }

            #shift_area {
                background-color: white;
                border-left: 1px solid #D7DEE5;
                border-right: 1px solid #D7DEE5;
            }

            #day_summary {
                background-color: white;
                border: 1px solid #D7DEE5;
            }
        """)

    def create_outside_period_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("day_header")

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(2, 2, 2, 2)
        header_layout.setSpacing(2)

        day_label = QLabel(
            self.day.date.toString("ddd").upper()
        )

        date_label = QLabel(
            self.day.date.toString("d MMM")
        )

        day_label.setAlignment(Qt.AlignCenter)
        date_label.setAlignment(Qt.AlignCenter)

        day_label.setStyleSheet("""
            QLabel {
                color: #B0B7BC;
                font-size: 10px;
                font-weight: 600;
            }
        """)

        date_label.setStyleSheet("""
            QLabel {
                color: #B0B7BC;
                font-size: 14px;
                font-weight: 600;
            }
        """)

        header_layout.addWidget(day_label)
        header_layout.addWidget(date_label)

        empty_area = QFrame()
        empty_area.setObjectName("outside_period")

        summary = QFrame()
        summary.setObjectName("day_summary")
        summary.setFixedHeight(50)

        layout.addWidget(header)
        layout.addWidget(empty_area, 1)
        layout.addWidget(summary)

        self.setStyleSheet("""
            #day_header {
                background-color: #F5F5F5;
                border: 1px solid #E1E1E1;
            }

            #outside_period {
                background-color: #F5F5F5;
                border-left: 1px solid #E1E1E1;
                border-right: 1px solid #E1E1E1;
            }

            #day_summary {
                background-color: #F5F5F5;
                border: 1px solid #E1E1E1;
            }
        """)

    @staticmethod
    def format_hours(hours):
        if hours.is_integer():
            return f"{int(hours)} hours"

        return f"{hours:g} hours"