from PySide6.QtCore import Signal, QDate, Qt, QTimer
from PySide6.QtWidgets import QWidget,QLabel,QComboBox,QDateEdit,QPushButton,QMessageBox,QVBoxLayout, QScrollArea, QSizePolicy, QLayout
from PySide6.QtUiTools import QUiLoader

from ui.holiday_card import HolidayCard
from ui.holiday_dialogue import HolidayDialogue


class ManageHolidaysPage(QWidget):

    back_clicked = Signal()

    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.templates = {}
        self.cards = []
        self.empty_label = None
        self.load_ui()
        self.find_widgets()
        self.setup_filters()
        self.connect_signals()
        self.load_employees()
        self.load_holidays()

    # UI
    def load_ui(self):
        loader = QUiLoader()
        self.ui = loader.load("ui_files/manage_holidays.ui", self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

    def find_widgets(self):
        self.back_button = self.ui.findChild(QPushButton,"back_button")
        self.employee_combo = self.ui.findChild(QComboBox,"employee_combo")
        self.from_date_edit = self.ui.findChild(QDateEdit,"from_date_edit")
        self.to_date_edit = self.ui.findChild(QDateEdit,"to_date_edit")
        self.clear_filters_button = self.ui.findChild(QPushButton,"clear_button")
        self.holiday_scroll_area = self.ui.findChild(QScrollArea,"holiday_scroll_area")
        self.holiday_list_widget = self.ui.findChild(QWidget,"scrollAreaWidgetContents")
        self.holiday_list_layout = self.ui.findChild(QVBoxLayout,"holiday_list_layout")
        self.add_holiday_button = self.ui.findChild(QPushButton,"add_holiday_button")

    # Setup
    def setup_filters(self):
        self.from_date_edit.setDate(QDate(2020, 1, 1))
        self.to_date_edit.setDate(QDate(2030, 1, 1))
        self.holiday_list_layout.setAlignment(Qt.AlignTop)
        self.holiday_list_layout.setSpacing(6)
        self.holiday_list_layout.setContentsMargins(0, 0, 0, 20)
        self.holiday_list_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.holiday_scroll_area.setWidgetResizable(True)
        self.holiday_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.holiday_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.holiday_list_widget.setMinimumHeight(0)
        self.holiday_list_widget.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        
    # Signals
    def connect_signals(self):
        self.back_button.clicked.connect(self.back_clicked.emit)
        self.add_holiday_button.clicked.connect(self.add_holiday)
        self.clear_filters_button.clicked.connect(self.clear_filters)
        self.employee_combo.currentIndexChanged.connect(self.apply_filters)
        self.from_date_edit.dateChanged.connect(self.apply_filters)
        self.to_date_edit.dateChanged.connect(self.apply_filters)

    # Employees
    def load_employees(self):
        self.employee_combo.blockSignals(True)
        self.employee_combo.clear()
        self.employee_combo.addItem("All employees", None)
        self.templates.clear()
        templates = self.database.get_templates()
        for template in templates:
            template_id = template[0]
            self.templates[template_id] = {"name": template[1],"colour": template[2],}
            self.employee_combo.addItem(template[1],template_id)
        self.employee_combo.blockSignals(False)

    # Holidays
    def load_holidays(self):
        self.clear_cards()
        selected_employee = self.employee_combo.currentData()
        holidays = []
        if selected_employee is None:
            templates = self.database.get_templates()
            for template in templates:
                template_id = template[0]
                holidays.extend(self.database.get_holidays(template_id))
        else:
            holidays = self.database.get_holidays(selected_employee)
        holidays.sort(
            key=lambda holiday: (
                holiday.start_date.toJulianDay(),
                holiday.id
            )
        )
        self.display_holidays(holidays)
        QTimer.singleShot(0, self.update_scroll_content)

    # Display
    def display_holidays(self, holidays):
        for holiday in holidays:
            template = self.templates.get(holiday.template_id)
            if template is None:
                continue
            card = HolidayCard(
                holiday=holiday,
                employee_name=template["name"],
                employee_colour=template["colour"]
            )
            card.edit_requested.connect(self.edit_holiday)
            card.delete_requested.connect(self.delete_holiday)
            self.holiday_list_layout.addWidget(card,0,Qt.AlignHCenter | Qt.AlignTop)
            self.cards.append(card)

        self.update_empty_state()

    # Clear cards
    def clear_cards(self):
        if self.empty_label is not None:
            self.empty_label.setParent(None)
            self.empty_label.deleteLater()
            self.empty_label = None

        while self.holiday_list_layout.count():
            item = self.holiday_list_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        self.cards.clear()

    # Empty state
    def update_empty_state(self):

        if (hasattr(self, "empty_label") and self.empty_label is not None):
            self.empty_label.deleteLater()
            self.empty_label = None
        if self.cards:
            return

        self.empty_label = QLabel("No holidays found.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet(
            """
            QLabel {
                color: #71808A;
                font-size: 12px;
                padding: 30px;
            }
            """
        )
        self.holiday_list_layout.addWidget(self.empty_label)

    # Add
    def add_holiday(self):
        dialog = HolidayDialogue(database=self.database,parent=self)
        dialog.saved.connect(self.create_holiday)
        dialog.exec()

    def create_holiday(self, data):
        self.database.add_holiday(
            template_id=data["template_id"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            start_time=data["start_time"],
            end_time=data["end_time"]
        )
        self.load_holidays()

    # Edit
    def edit_holiday(self, holiday_id):
        holiday = self.database.get_holiday(holiday_id)

        if holiday is None:
            return

        dialog = HolidayDialogue(
            database=self.database,
            holiday=holiday,
            parent=self
        )

        dialog.saved.connect(
            lambda data: self.update_holiday(
                holiday_id,
                data
            )
        )
        dialog.exec()

    def update_holiday(self, holiday_id, data):
        self.database.update_holiday(
            holiday_id=holiday_id,
            template_id=data["template_id"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            start_time=data["start_time"],
            end_time=data["end_time"]
        )
        self.load_holidays()

    # Delete
    def delete_holiday(self, holiday_id):
        holiday = self.database.get_holiday(holiday_id)
        if holiday is None:
            return
        template = self.templates.get(holiday.template_id)
        employee_name = (
            template["name"]
            if template is not None
            else "this employee"
        )

        reply = QMessageBox.question(
            self,
            "Delete Holiday",
            (
                f"Are you sure you want to delete the holiday "
                f"for {employee_name}?\n\n"
                f"This action cannot be undone."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return
        self.database.delete_holiday(holiday_id)
        self.load_holidays()

    # Filters
    def apply_filters(self):
        self.clear_cards()
        selected_employee = self.employee_combo.currentData()
        from_date = self.from_date_edit.date()
        to_date = self.to_date_edit.date()
        holidays = []

        if selected_employee is None:
            templates = self.database.get_templates()
            for template in templates:
                holidays.extend(self.database.get_holidays(template[0]))
        else:
            holidays = self.database.get_holidays(selected_employee)
        filtered = []

        for holiday in holidays:
            if holiday.end_date < from_date:
                continue
            if holiday.start_date > to_date:
                continue
            filtered.append(holiday)
        filtered.sort(
            key=lambda holiday: (
                holiday.start_date.toJulianDay(),
                holiday.id
            )
        )
        self.display_holidays(filtered)
        QTimer.singleShot(0, self.update_scroll_content)

    def clear_filters(self):
        self.employee_combo.blockSignals(True)
        self.employee_combo.setCurrentIndex(0)
        self.employee_combo.blockSignals(False)

        # Use the full QDate range rather than today's date
        self.from_date_edit.blockSignals(True)
        self.to_date_edit.blockSignals(True)
        self.from_date_edit.setDate(QDate(2000, 1, 1))
        self.to_date_edit.setDate(QDate(2100, 12, 31))
        self.from_date_edit.blockSignals(False)
        self.to_date_edit.blockSignals(False)
        self.load_holidays()

    def update_scroll_content(self):
        self.holiday_list_layout.invalidate()
        self.holiday_list_layout.activate()

        content_height = self.holiday_list_layout.sizeHint().height()

        self.holiday_list_widget.setMinimumHeight(content_height)
        self.holiday_list_widget.updateGeometry()

    