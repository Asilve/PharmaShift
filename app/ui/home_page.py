from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtUiTools import QUiLoader

class HomePage(QWidget):

    generate_schedule_clicked = Signal()
    saved_schedule_clicked = Signal()
    manage_templates_clicked = Signal()
    manage_holidays_clicked = Signal()
    exit_clicked = Signal()

    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        self.ui = loader.load("ui_files/home.ui", None)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # Buttons
        self.generate_schedule_button = self.ui.findChild(QPushButton,"schedule_button")
        self.saved_schedule_button = self.ui.findChild(QPushButton, "saved_schedule_button")
        self.manage_template_button = self.ui.findChild(QPushButton, "templates_button")
        self.manage_holidays_button = self.ui.findChild(QPushButton, "holidays_button")
        self.exit_button = self.ui.findChild(QPushButton, "exit_button")

        # Button Signals
        self.generate_schedule_button.clicked.connect(self.generate_schedule_clicked.emit)
        self.saved_schedule_button.clicked.connect(self.saved_schedule_clicked.emit)
        self.manage_template_button.clicked.connect(self.manage_templates_clicked.emit)
        self.manage_holidays_button.clicked.connect(self.manage_holidays_clicked.emit)
        self.exit_button.clicked.connect(self.exit_clicked.emit)