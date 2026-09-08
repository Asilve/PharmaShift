from PySide6.QtCore import Signal, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLayout
from PySide6.QtWidgets import QApplication

from models.template import EmployeeTemplate
from ui.template_card import TemplateCard


class ManageTemplatesPage(QWidget):

    back_clicked = Signal()

    def __init__(self, database):
        super().__init__()

        self.database = database

        loader = QUiLoader()
        self.ui = loader.load("ui_files/manage_templates.ui", None)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.back_button = self.ui.findChild(QPushButton,"back_button")

        self.back_button.clicked.connect(self.back_clicked.emit)

        self.template_list_layout = self.ui.findChild(QLayout,"template_list_layout")

        self.template_list_layout.setAlignment(Qt.AlignTop)

        self.load_templates()

    def load_templates(self):
        templates = self.database.get_templates()

        for template_data in templates:
            template = EmployeeTemplate(name=template_data[1], colour=template_data[2])

            card = TemplateCard(template)

            self.template_list_layout.addWidget(card,0,Qt.AlignHCenter | Qt.AlignTop)
