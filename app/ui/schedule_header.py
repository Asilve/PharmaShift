from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QSizePolicy
from PySide6.QtCore import Qt


class ScheduleHeader(QWidget):

    def __init__(self, schedule):
        super().__init__()

        self.schedule = schedule
        self.setObjectName("schedule_header")
        self.setup_ui()

    def setup_ui(self):

        header_frame = QFrame()
        header_frame.setObjectName("header_frame")

        header_frame.setStyleSheet("""
            #header_frame {
                background-color: white;
                border: 1px solid #D7DEE5;
                border-radius: 8px;
            }
        """)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(12)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(header_frame)

        colour_bar = QFrame()
        colour_bar.setFixedWidth(6)
        colour_bar.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Preferred)

        colour_bar.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.schedule.template.colour};
                border-radius: 3px;
            }}
            """
        )

        information_layout = QVBoxLayout()
        information_layout.setContentsMargins(0, 0, 0, 0)
        information_layout.setSpacing(2)

        name_label = QLabel(self.schedule.template.name)

        name_label.setStyleSheet("""
            QLabel {
                color: #263238;
                font-size: 20px;
                font-weight: 700;
            }
        """)

        information_layout.addWidget(name_label)
        notes = self.schedule.template.notes

        if notes:
            notes_label = QLabel(notes)
            notes_label.setStyleSheet("""
                QLabel {
                    color: #71808A;
                    font-size: 11px;
                }
            """)

            information_layout.addWidget(notes_label)

        information_layout.addStretch()
        header_layout.addWidget(colour_bar)
        header_layout.addLayout(information_layout)

        date_range_label = QLabel(
            f"{self.schedule.start_date.toString('d MMM yyyy')} - "
            f"{self.schedule.end_date.toString('d MMM yyyy')}"
        )

        date_range_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        date_range_label.setStyleSheet("""
            QLabel {
                color: #52636F;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        header_layout.addStretch()
        header_layout.addWidget(date_range_label)

        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.setFixedHeight(65)