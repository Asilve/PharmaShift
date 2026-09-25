from PySide6.QtCore import Signal, QDate, QTime, QObject
from PySide6.QtWidgets import QLabel,QComboBox,QDateEdit,QTimeEdit,QRadioButton,QCheckBox,QLineEdit,QPushButton,QWidget,QMessageBox,QAbstractSpinBox
from PySide6.QtUiTools import QUiLoader

from services.holiday_validator import HolidayValidator


class HolidayDialogue(QObject):

    saved = Signal(dict)

    def __init__(self,database,holiday=None,parent=None):
        super().__init__(parent)
        self.database = database
        self.holiday = holiday

        self.load_ui()
        self.find_widgets()
        self.populate_employees()
        self.connect_signals()
        self.setup_initial_state()
        if self.holiday is not None:
            self.load_holiday()

    # UI
    def load_ui(self):
        loader = QUiLoader()
        self.ui = loader.load("ui_files/holiday_dialogue.ui")

    def find_widgets(self):
        self.title_label = self.ui.findChild(QLabel, "title_label")
        self.employee_combo = self.ui.findChild(QComboBox, "employee_combo")
        self.period_radio = self.ui.findChild(QRadioButton, "period_radio")
        self.single_day_radio = self.ui.findChild(QRadioButton, "single_day_radio")
        self.period_widget = self.ui.findChild(QWidget, "period_widget")
        self.single_day_widget = self.ui.findChild(QWidget, "single_day_widget")
        self.from_date_edit = self.ui.findChild(QDateEdit, "from_date_edit")
        self.to_date_edit = self.ui.findChild(QDateEdit, "to_date_edit")
        self.date_edit = self.ui.findChild(QDateEdit, "date_edit")

        self.duration_widget = self.ui.findChild(QWidget, "duration_widget")
        self.full_day_radio = self.ui.findChild(QRadioButton, "full_day_radio")
        self.partial_day_radio = self.ui.findChild(QRadioButton, "partial_day_radio")
        self.partial_day_widget = self.ui.findChild(QWidget, "partial_day_widget")

        self.start_time_edit = self.ui.findChild(QTimeEdit, "start_time_edit")
        self.end_time_edit = self.ui.findChild(QTimeEdit, "end_time_edit")
        self.cancel_button = self.ui.findChild(QPushButton, "cancel_button")
        self.save_button = self.ui.findChild(QPushButton, "save_button")
        self.date_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.from_date_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.to_date_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)

    # Setup
    def setup_initial_state(self):
        self.single_day_radio.setChecked(True)
        self.full_day_radio.setChecked(True)
        self.period_widget.setVisible(False)
        self.single_day_widget.setVisible(True)
        self.partial_day_widget.setVisible(False)
        today = QDate.currentDate()
        self.date_edit.setDate(today)
        self.from_date_edit.setDate(today)
        self.to_date_edit.setDate(today)
        self.start_time_edit.setTime(QTime(9, 0))
        self.end_time_edit.setTime(QTime(17, 0))
        if self.holiday is None:
            self.title_label.setText("Add Holiday")
        else:
            self.title_label.setText("Edit Holiday")

    # Employees
    def populate_employees(self):
        self.employee_combo.clear()
        templates = self.database.get_templates()
        for template in templates:
            template_id = template[0]
            name = template[1]
            self.employee_combo.addItem(name,template_id)

    # Signals
    def connect_signals(self):
        self.period_radio.toggled.connect(self.update_holiday_type)
        self.single_day_radio.toggled.connect(self.update_holiday_type)
        self.full_day_radio.toggled.connect(self.update_duration)
        self.partial_day_radio.toggled.connect(self.update_duration)
        self.cancel_button.clicked.connect(self.ui.reject)
        self.save_button.clicked.connect(self.save)

    # Visibility
    def update_holiday_type(self):
        if self.period_radio.isChecked():
            self.period_widget.setVisible(True)
            self.single_day_widget.setVisible(False)
            self.full_day_radio.setChecked(True)
            self.duration_widget.setEnabled(False)
            self.partial_day_widget.setVisible(True)
            self.partial_day_widget.setEnabled(False)

        else:
            self.period_widget.setVisible(False)
            self.single_day_widget.setVisible(True)
            self.duration_widget.setEnabled(True)
            self.update_duration()

    def update_duration(self):
        if not self.single_day_radio.isChecked():
            self.partial_day_widget.setEnabled(False)
            return
        self.partial_day_widget.setVisible(True)
        self.partial_day_widget.setEnabled(
            self.partial_day_radio.isChecked()
        )

    # Edit
    def load_holiday(self):
        holiday = self.holiday
        index = self.employee_combo.findData(holiday.template_id)
        if index >= 0:
            self.employee_combo.setCurrentIndex(index)
        if holiday.start_date != holiday.end_date:
            self.period_radio.setChecked(True)
            self.from_date_edit.setDate(holiday.start_date)
            self.to_date_edit.setDate(holiday.end_date)
        else:
            self.single_day_radio.setChecked(True)
            self.date_edit.setDate(holiday.start_date)
            if (holiday.start_time is not None and holiday.end_time is not None):
                self.partial_day_radio.setChecked(True)
                self.start_time_edit.setTime(QTime.fromString(holiday.start_time,"HH:mm"))
                self.end_time_edit.setTime(QTime.fromString(holiday.end_time,"HH:mm"))
            else:
                self.full_day_radio.setChecked(True)
        self.update_holiday_type()
        self.update_duration()

    # Form data
    def get_form_data(self):

        template_id = self.employee_combo.currentData()

        if self.period_radio.isChecked():

            start_date = self.from_date_edit.date()
            end_date = self.to_date_edit.date()

            start_time = None
            end_time = None

        else:

            start_date = self.date_edit.date()
            end_date = self.date_edit.date()

            if self.partial_day_radio.isChecked():

                start_time = (
                    self.start_time_edit.time()
                    .toString("HH:mm")
                )

                end_time = (
                    self.end_time_edit.time()
                    .toString("HH:mm")
                )

            else:

                start_time = None
                end_time = None

        return {
            "template_id": template_id,
            "start_date": start_date,
            "end_date": end_date,
            "start_time": start_time,
            "end_time": end_time
        }

    # Save
    def save(self):
        data = self.get_form_data()
        errors = HolidayValidator.validate(
            start_date=data["start_date"],
            end_date=data["end_date"],
            start_time=data["start_time"],
            end_time=data["end_time"]
        )
        if errors:
            self.show_validation_errors(errors)
            return
        self.saved.emit(data)
        self.ui.accept()

    # Validation
    def show_validation_errors(self, errors):
        message = "\n".join(f"• {error}" for error in errors)
        QMessageBox.warning(
            self.ui,
            "Invalid Holiday",
            message
        )

    # Execute dialog
    def exec(self):
        return self.ui.exec()
    