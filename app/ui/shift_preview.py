from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy


class ShiftPreview(QWidget):

    def __init__(self, shift):
        super().__init__()
        self.shift = shift
        self.setup_ui()

    def setup_ui(self):
        frame = QFrame()
        frame.setObjectName("shift_frame")

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(4, 4, 4, 4)
        frame_layout.setSpacing(2)

        name_label = QLabel(self.shift.location)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("""
            QLabel {
                color: #263238;
                font-size: 11px;
                font-weight: 600;
            }
        """)
        frame_layout.addWidget(name_label)

        if (
            self.shift.start_time is not None
            and self.shift.end_time is not None
        ):
            time_label = QLabel(
                f"{self.shift.start_time} - "
                f"{self.shift.end_time}"
            )

            time_label.setStyleSheet("""
                QLabel {
                    color: #52636F;
                    font-size: 9px;
                }
            """)

            frame_layout.addWidget(time_label)

        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(4)

        hours_label = QLabel(
            self.format_hours(self.shift.hours)
        )

        rate_label = QLabel(
            f"£{self.shift.rate:.2f}/hr"
        )

        hours_label.setStyleSheet("""
            QLabel {
                color: #52636F;
                font-size: 9px;
            }
        """)

        rate_label.setStyleSheet("""
            QLabel {
                color: #52636F;
                font-size: 9px;
            }
        """)

        details_layout.addWidget(hours_label)
        details_layout.addStretch()
        details_layout.addWidget(rate_label)

        frame_layout.addLayout(details_layout)

        total_pay = self.shift.hours * self.shift.rate

        pay_label = QLabel(
            f"Total: £{total_pay:.2f}"
        )

        pay_label.setAlignment(Qt.AlignRight)

        pay_label.setStyleSheet("""
            QLabel {
                color: #263238;
                font-size: 10px;
                font-weight: 600;
            }
        """)

        frame_layout.addWidget(pay_label)

        frame.setStyleSheet("""
            #shift_frame {
                background-color: #F4F7FA;
                border: 1px solid #BFC9D1;
                border-radius: 7px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(frame)

        self.setSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Minimum
        )

    @staticmethod
    def format_hours(hours):
        if hours is None:
            return "0 hours"

        if hours.is_integer():
            return f"{int(hours)} hours"

        return f"{hours:g} hours"