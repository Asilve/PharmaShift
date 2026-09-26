from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
    QCheckBox,
    QLineEdit
)


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

        # Location
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

        # Time
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

        # Hours / holiday information / rate
        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(4)

        if self.shift.holiday_affected:
            hours_label = QLabel(
                f"H: {self.format_hours_short(self.shift.holiday_hours)}"
                f" | "
                f"W: {self.format_hours_short(self.shift.worked_hours)}"
            )
        else:
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

        # Pay is based on worked hours
        total_pay = self.shift.worked_hours * self.shift.rate

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

        # Coverage
        if self.shift.holiday_affected:
            coverage_layout = QHBoxLayout()
            coverage_layout.setContentsMargins(0, 2, 0, 0)
            coverage_layout.setSpacing(4)

            self.covered_checkbox = QCheckBox("")
            self.covered_checkbox.setChecked(self.shift.covered)

            self.covered_by_edit = QLineEdit()
            self.covered_by_edit.setPlaceholderText("Covered By")
            self.covered_by_edit.setText(self.shift.covered_by)

            self.covered_by_edit.setEnabled(self.shift.covered)

            self.covered_checkbox.setStyleSheet("""
                QCheckBox {
                    color: #52636F;
                    font-size: 9px;
                }
            """)

            self.covered_by_edit.setStyleSheet("""
                QLineEdit {
                    color: #263238;
                    font-size: 9px;
                    padding: 2px 4px;
                    border: 1px solid #BFC9D1;
                    border-radius: 4px;
                    background-color: white;
                }

                QLineEdit:disabled {
                    color: #9AA5AB;
                    background-color: #E9EDF0;
                }
            """)

            coverage_layout.addWidget(self.covered_checkbox)
            coverage_layout.addWidget(self.covered_by_edit)

            frame_layout.addLayout(coverage_layout)

            self.covered_checkbox.toggled.connect(
                self.coverage_toggled
            )

            self.covered_by_edit.textChanged.connect(
                self.coverage_by_changed
            )

        if not self.shift.holiday_affected:
            background_colour = "#F4F7FA"
            border_colour = "#BFC9D1"

        elif self.shift.worked_hours <= 0:
            background_colour = "#FFF1F1"
            border_colour = "#E3B4B4"

        else:
            background_colour = "#FFF8E8"
            border_colour = "#E5C985"

        frame.setStyleSheet(f"""
            #shift_frame {{
                background-color: {background_colour};
                border: 1px solid {border_colour};
                border-radius: 7px;
            }}
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

    @staticmethod
    def format_hours_short(hours):
        if hours is None:
            return "0h"

        if hours.is_integer():
            return f"{int(hours)}h"

        return f"{hours:g}h"

    def coverage_toggled(self, checked):
        self.shift.covered = checked
        self.covered_by_edit.setEnabled(checked)

        if not checked:
            self.shift.covered_by = ""
            self.covered_by_edit.clear()

    def coverage_by_changed(self, text):
        self.shift.covered_by = text
