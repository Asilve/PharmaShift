from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

from models.template import EmployeeTemplate


class TemplateCard(QWidget):
    def __init__(self, template: EmployeeTemplate):
        super().__init__()

        self.setFixedSize(1180, 80)

        loader = QUiLoader()
        self.ui = loader.load("ui_files/template_card.ui")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)


        self.name_label = self.ui.findChild(QLabel,"name_label")

        self.subtitle_label = self.ui.findChild(QLabel,"subtitle_label")

        self.colour_indicator = self.ui.findChild(QFrame,"colour_indicator")

        self.set_template(template)

    def set_template(self, template):
        self.template = template

        self.name_label.setText(template.name)
        self.subtitle_label.setText("Pharmacist Template")

        self.colour_indicator.setStyleSheet(
            f"background-color: {template.colour};"
        )