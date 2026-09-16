from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame, QSizePolicy
from PySide6.QtCore import Qt



class PreviewPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.page_frame = QFrame()
        self.page_frame.setObjectName("page_frame")
        self.page_frame.setFixedSize(1000, 707)
        self.page_frame.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)

        self.page_frame.setStyleSheet("""
            #page_frame {
                background-color: white;
                border: 1px solid #C8C8C8;
            }
        """)

        self.page_layout = QVBoxLayout(self.page_frame)
        self.page_layout.setContentsMargins(20, 20, 20, 20)
        self.page_layout.setSpacing(10)

        layout.addWidget(
            self.page_frame,
            alignment=Qt.AlignHCenter
        )