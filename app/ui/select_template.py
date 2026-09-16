from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLayout, QSizePolicy
from PySide6.QtUiTools import QUiLoader

from models.template import EmployeeTemplate
from ui.template_card import TemplateCard


class SelectTemplatePage(QWidget):

    back_clicked = Signal()
    continue_clicked = Signal(object)

    def __init__(self, database):
        super().__init__()

        self.database = database

        # Card selection
        self.selected_card = None
        self.selected_template = None

        loader = QUiLoader()
        self.ui = loader.load("ui_files/select_template.ui", None)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # Back Button
        self.back_button = self.ui.findChild(QPushButton, "back_button")
        self.back_button.clicked.connect(self.back_clicked.emit)

        # Continue Button
        self.continue_button = self.ui.findChild(QPushButton,"continue_button")
        self.continue_button.clicked.connect(self.continue_to_dates)

        # Template list layout
        self.template_list_layout = self.ui.findChild(QLayout,"template_list_layout")
        self.template_list_layout.setAlignment(Qt.AlignTop)
        self.template_list_layout.setSpacing(6)
        self.template_list_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        # Scroll Area / Content
        self.ui.scrollArea.setWidgetResizable(True)
        self.ui.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.scroll_content = self.ui.findChild(QWidget,"scroll_content")
        self.scroll_content.setMinimumHeight(0)
        self.scroll_content.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)

        # Continue disabled until a template is selected
        self.continue_button.setEnabled(False)

        self.load_templates()

    def load_templates(self):
        # Remember which template was selected, if any
        selected_template_id = (
            self.selected_template.id
            if self.selected_template is not None
            else None
        )

        # Forget the old card before deleting it
        self.selected_card = None

        self.clear_template_cards()

        templates = self.database.get_templates()

        for template_data in templates:
            template = EmployeeTemplate(
                name=template_data[1],
                colour=template_data[2],
                notes=template_data[3],
                template_id=template_data[0]
            )

            card = TemplateCard(template)

            card.clicked.connect(
                lambda checked=False, card=card:
                self.select_template(card)
            )

            self.template_list_layout.addWidget(
                card, 0, Qt.AlignHCenter | Qt.AlignTop
            )

            # Restore the previous selection
            if template.id == selected_template_id:
                self.selected_card = card
                self.selected_template = template
                card.set_selected(True)

        self.template_list_layout.invalidate()
        self.template_list_layout.activate()

        self.scroll_content.setMinimumHeight(
            self.template_list_layout.sizeHint().height()
        )

        self.continue_button.setEnabled(
            self.selected_template is not None
        )

    def select_template(self, card):
        if self.selected_card is not None:
            self.selected_card.set_selected(False)

        self.selected_card = card
        self.selected_card.set_selected(True)

        self.selected_template = card.template

        self.continue_button.setEnabled(True)

    def continue_to_dates(self):
        if self.selected_template is None:
            return

        self.continue_clicked.emit(self.selected_template)

    def clear_template_cards(self):
        while self.template_list_layout.count():
            item = self.template_list_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()