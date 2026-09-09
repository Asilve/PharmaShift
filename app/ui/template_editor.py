from PySide6.QtCore import Signal
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QFrame, QColorDialog, QMessageBox


class TemplateEditorPage(QWidget):

    saved = Signal()
    back_clicked = Signal()

    def __init__(self, database):
        super().__init__()

        self.database = database
        self.template = None

        # Employee Details
        self.employee_colour = "#FFFFFF"

        loader = QUiLoader()
        self.ui = loader.load("ui_files/template_editor.ui", None)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        # back button
        self.back_button = self.ui.findChild(QPushButton, "back_button")
        self.back_button.clicked.connect(self.back_clicked.emit)

        # Line Edits
        self.employee_name = self.ui.findChild(QLineEdit, "name_edit")
        self.employee_notes = self.ui.findChild(QLineEdit, "notes_edit")

        # Colour
        self.employee_colour_preview = self.ui.findChild(QFrame, "colour_preview")
        self.colour_button = self.ui.findChild(QPushButton, "colour_button")
        self.colour_button.clicked.connect(self.select_colour)

        # Save Button
        self.save_button = self.ui.findChild(QPushButton, "save_button")
        self.save_button.clicked.connect(self.save_template)



    def set_template(self, template):
        self.template = template
        if template is None:
            self.employee_name.setText("")
            self.employee_notes.setText("")
            self.employee_colour = "#FFFFFF"
            self.employee_colour_preview.setStyleSheet(f"background-color: {self.employee_colour};")

        else:
            self.employee_name.setText(self.template.name)
            self.employee_notes.setText(self.template.notes)
            self.employee_colour = template.colour
            self.employee_colour_preview.setStyleSheet(f"background-color: {self.employee_colour};")

    def select_colour(self):
        colour = QColorDialog.getColor()

        if colour.isValid():
            self.employee_colour = colour.name().upper()

            self.employee_colour_preview.setStyleSheet(f"background-color: {self.employee_colour};")

    def save_template(self):
        name = self.employee_name.text().strip()
        notes = self.employee_notes.text().strip()
        colour = self.employee_colour

        if len(name) < 3:
            QMessageBox.warning(self,"Invalid Name","The pharmacist name must be at least 3 characters long.")
            return

        if self.template is None:
            # Add new template
            self.database.add_template(name, notes, colour)

        else:
            # Update existing template
            self.database.update_template(
                self.template.id,
                name,
                notes,
                colour
            )

            # Update the in-memory template object
            self.template.name = name
            self.template.notes = notes
            self.template.colour = colour

        self.saved.emit()