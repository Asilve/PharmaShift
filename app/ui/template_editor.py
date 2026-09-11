from PySide6.QtCore import Signal, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QFrame, QColorDialog, QMessageBox, QLayout, QSizePolicy


from ui.shift_card import ShiftCard
from ui.add_shift_card import AddShiftCard


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

        # Back button
        self.back_button = self.ui.findChild(QPushButton, "back_button")
        self.back_button.clicked.connect(self.back_clicked.emit)

        # Line Edits
        self.employee_name = self.ui.findChild(QLineEdit, "name_edit")
        self.employee_notes = self.ui.findChild(QLineEdit, "notes_edit")

        # Colour
        self.employee_colour_preview = self.ui.findChild(
            QFrame,
            "colour_preview"
        )
        self.colour_button = self.ui.findChild(
            QPushButton,
            "colour_button"
        )
        self.colour_button.clicked.connect(self.select_colour)

        # Save Button
        self.save_button = self.ui.findChild(QPushButton, "save_button")
        self.save_button.clicked.connect(self.save_template)

        # Day Layouts
        self.day_layouts = {
            0: self.ui.findChild(QLayout, "monday_shift_layout"),
            1: self.ui.findChild(QLayout, "tuesday_shift_layout"),
            2: self.ui.findChild(QLayout, "wednesday_shift_layout"),
            3: self.ui.findChild(QLayout, "thursday_shift_layout"),
            4: self.ui.findChild(QLayout, "friday_shift_layout"),
            5: self.ui.findChild(QLayout, "saturday_shift_layout"),
            6: self.ui.findChild(QLayout, "sunday_shift_layout"),
        }

        # Scroll Content
        self.day_scroll_contents = {
            0: self.ui.findChild(QWidget, "monday_scroll_content"),
            1: self.ui.findChild(QWidget, "tuesday_scroll_content"),
            2: self.ui.findChild(QWidget, "wednesday_scroll_content"),
            3: self.ui.findChild(QWidget, "thursday_scroll_content"),
            4: self.ui.findChild(QWidget, "friday_scroll_content"),
            5: self.ui.findChild(QWidget, "saturday_scroll_content"),
            6: self.ui.findChild(QWidget, "sunday_scroll_content"),
        }

        # Make each scroll content widget manage its existing
        # Designer-generated layout container.
        self.setup_scroll_contents()

    def setup_scroll_contents(self):
        for day, shift_layout in self.day_layouts.items():

            scroll_content = self.day_scroll_contents[day]

            # The actual QWidget containing the Designer layout.
            container = shift_layout.parentWidget()

            # Let the container grow with the scroll content.
            container.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Expanding
            )

            # scroll_content currently has no layout.
            # Give it one so the container is resized correctly.
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setContentsMargins(0, 0, 0, 0)
            scroll_layout.setSpacing(0)

            scroll_layout.addWidget(container)

    def set_template(self, template):
        self.template = template

        if template is None:
            self.employee_name.setText("")
            self.employee_notes.setText("")
            self.employee_colour = "#FFFFFF"

            self.employee_colour_preview.setStyleSheet(
                f"background-color: {self.employee_colour};"
            )

        else:
            self.employee_name.setText(self.template.name)
            self.employee_notes.setText(self.template.notes)
            self.employee_colour = template.colour

            self.employee_colour_preview.setStyleSheet(
                f"background-color: {self.employee_colour};"
            )

        self.load_shifts()

    def select_colour(self):
        colour = QColorDialog.getColor()

        if colour.isValid():
            self.employee_colour = colour.name().upper()

            self.employee_colour_preview.setStyleSheet(
                f"background-color: {self.employee_colour};"
            )

    def save_template(self):
        name = self.employee_name.text().strip()
        notes = self.employee_notes.text().strip()
        colour = self.employee_colour

        if len(name) < 3:
            QMessageBox.warning(
                self,
                "Invalid Name",
                "The pharmacist name must be at least 3 characters long."
            )
            return

        if self.template is None:
            # Add new template
            self.database.add_template(
                name,
                notes,
                colour
            )

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

    def load_shifts(self):

        # Clear existing cards
        for layout in self.day_layouts.values():

            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(6)
            layout.setAlignment(Qt.AlignTop)

            while layout.count():
                item = layout.takeAt(0)

                widget = item.widget()

                if widget is not None:
                    widget.deleteLater()

        if self.template is None:
            return

        # Add shift cards
        for shift in self.template.shifts:

            shift_card = ShiftCard(shift)

            self.day_layouts[shift.day_of_week].addWidget(
                shift_card,
                0,
                Qt.AlignTop
            )

        # Update each scroll area's content height
        for day, layout in self.day_layouts.items():
            add_card = AddShiftCard()

            add_card.clicked.connect(lambda day=day: self.add_shift(day))
            layout.addWidget(add_card,0,Qt.AlignTop)

            layout.setAlignment(Qt.AlignTop)
            layout.invalidate()
            layout.activate()

            scroll_content = self.day_scroll_contents[day]

            required_height = layout.sizeHint().height()

            scroll_content.setMinimumHeight(
                required_height
            )