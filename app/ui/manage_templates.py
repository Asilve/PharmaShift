from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLayout

from models.template import EmployeeTemplate
from ui.template_card import TemplateCard


class ManageTemplatesPage(QWidget):

    back_clicked = Signal()

    def __init__(self, database):
        super().__init__()

        self.database = database

        # Card selection
        self.selected_card = None

        loader = QUiLoader()
        self.ui = loader.load("ui_files/manage_templates.ui", None)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)
        self.ui.scrollArea.viewport().installEventFilter(self)

        # Event filters for clearing selection
        self.installEventFilter(self)
        self.ui.installEventFilter(self)
        self.ui.scrollArea.viewport().installEventFilter(self)

        # Back Button
        self.back_button = self.ui.findChild(QPushButton,"back_button")
        self.back_button.clicked.connect(self.back_clicked.emit)

        # Layout template list
        self.template_list_layout = self.ui.findChild(QLayout,"template_list_layout")
        self.template_list_layout.setAlignment(Qt.AlignTop)

        # Buttons
        self.edit_button = self.ui.findChild(QPushButton, "edit_button")
        self.delete_button = self.ui.findChild(QPushButton, "delete_button")
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)

        self.load_templates()

        

    def load_templates(self):
        templates = self.database.get_templates()

        for template_data in templates:
            template = EmployeeTemplate(name=template_data[1], colour=template_data[2])

            card = TemplateCard(template)

            card.clicked.connect(lambda checked=False, card=card: self.select_template(card))

            self.template_list_layout.addWidget(card,0,Qt.AlignHCenter | Qt.AlignTop)


    def select_template(self, card):
        if self.selected_card is not None:
            self.selected_card.set_selected(False)

        self.selected_card = card
        self.selected_card.set_selected(True)

        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)


    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            if watched == self.ui.scrollArea.viewport():
                self.clear_selection()

        return super().eventFilter(watched, event)

    def clear_selection(self):
        if self.selected_card is not None:
            self.selected_card.set_selected(False)
            self.selected_card = None

        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def mousePressEvent(self, event):
        self.clear_selection()
        super().mousePressEvent(event)

