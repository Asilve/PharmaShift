from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class TemplateEditorPage(QWidget):

    saved = Signal()
    back_clicked = Signal()

    def __init__(self, database):
        super().__init__()

        self.database = database
        self.template = None

        loader = QUiLoader()
        self.ui = loader.load("ui_files/template_editor.ui", None)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # back button
        self.back_button = self.ui.findChild(QPushButton, "back_button")
        self.back_button.clicked.connect(self.back_clicked.emit)


    def set_template(self, template):
        self.template = template
        if template is None:
            print(self.template)
        else:
            self.template = template
            print(self.template)