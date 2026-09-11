from PySide6.QtCore import Qt, QTime, Signal, QEvent
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog, QLineEdit, QComboBox, QTimeEdit, QDoubleSpinBox, QCheckBox, QPushButton, QLabel, QMessageBox, QVBoxLayout

from models.shift import Shift


class ShiftEditorDialog(QDialog):

    saved = Signal(object)
    deleted = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        loader = QUiLoader()
        self.ui = loader.load("ui_files/shift_editor.ui", None)
        self.ui.installEventFilter(self)
        self.setObjectName("shift_editor")
        self.setWindowTitle("Shift Editor")
        self.setFixedSize(self.ui.size())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.setWindowModality(Qt.ApplicationModal)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.shift = None
        self.edit_mode = False

        self.title_label = self.ui.findChild(QLabel,"title_label")
        self.shift_name_edit = self.ui.findChild(QLineEdit,"shift_name_edit")
        self.day_combo = self.ui.findChild(QComboBox,"day_combo")
        self.flexible_hours_check = self.ui.findChild(QCheckBox,"flexible_hours_check")
        self.start_time_edit = self.ui.findChild(QTimeEdit,"start_time_edit")
        self.end_time_edit = self.ui.findChild(QTimeEdit,"end_time_edit")
        self.hours_spinbox = self.ui.findChild(QDoubleSpinBox,"hours_spinbox")
        self.rate_spinbox = self.ui.findChild(QDoubleSpinBox,"rate_spinbox")
        self.delete_button = self.ui.findChild(QPushButton,"delete_button")
        self.cancel_button = self.ui.findChild(QPushButton,"cancel_button")
        self.save_button = self.ui.findChild(QPushButton,"save_button")

        self.days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        self.day_combo.addItems(self.days)

        self.flexible_hours_check.toggled.connect(self.update_time_mode)
        self.start_time_edit.timeChanged.connect(self.update_timed_hours)
        self.end_time_edit.timeChanged.connect(self.update_timed_hours)
        self.save_button.clicked.connect(self.save_shift)
        self.cancel_button.clicked.connect(self.cancel)
        self.delete_button.clicked.connect(self.delete_shift)

        self.save_button.setDefault(True)
        self.save_button.setAutoDefault(True)

        self.cancel_button.setAutoDefault(False)
        self.delete_button.setAutoDefault(False)

        self.delete_button.hide()

        self.update_time_mode(False)


    def set_shift(self, shift=None, day=None):
        self.shift = shift

        if shift is None:
            self.edit_mode = False

            self.title_label.setText("Add New Shift")
            self.delete_button.hide()

            self.shift_name_edit.clear()

            if day is not None:
                self.day_combo.setCurrentIndex(day)
            else:
                self.day_combo.setCurrentIndex(0)

            self.flexible_hours_check.setChecked(False)
            self.start_time_edit.setTime(QTime(9, 0))
            self.end_time_edit.setTime(QTime(17, 0))
            self.hours_spinbox.setValue(8.0)
            self.rate_spinbox.setValue(0.0)

        else:
            self.edit_mode = True

            self.title_label.setText("Edit Shift")
            self.delete_button.show()

            self.shift_name_edit.setText(shift.location)
            self.day_combo.setCurrentIndex(shift.day_of_week)

            flexible = shift.start_time is None and shift.end_time is None
            self.flexible_hours_check.setChecked(flexible)

            if flexible:
                self.hours_spinbox.setValue(float(shift.hours))

            else:
                start_time = QTime.fromString(shift.start_time,"HH:mm")
                end_time = QTime.fromString(shift.end_time,"HH:mm")

                self.start_time_edit.setTime(start_time)
                self.end_time_edit.setTime(end_time)
                self.hours_spinbox.setValue(float(shift.hours))

            self.rate_spinbox.setValue(float(shift.rate))

        self.update_time_mode(self.flexible_hours_check.isChecked())


    def update_time_mode(self, flexible):
        self.start_time_edit.setEnabled(not flexible)
        self.end_time_edit.setEnabled(not flexible)
        self.hours_spinbox.setEnabled(flexible)

        if not flexible:
            self.update_timed_hours()

    def update_timed_hours(self):
        if self.flexible_hours_check.isChecked():
            return

        start = self.start_time_edit.time()
        end = self.end_time_edit.time()

        if end <= start:
            self.hours_spinbox.setValue(0.0)
            return

        seconds = start.secsTo(end)
        hours = seconds / 3600

        self.hours_spinbox.setValue(hours)


    def validate(self):
        name = self.shift_name_edit.text().strip()

        if len(name) < 3:
            QMessageBox.warning(self,"Invalid Shift Name","The shift name must be at least 3 characters long.")
            self.shift_name_edit.setFocus()
            return False

        rate = self.rate_spinbox.value()
        if rate <= 0:
            QMessageBox.warning(self,"Invalid Rate","The hourly rate must be greater than £0.")
            self.rate_spinbox.setFocus()
            return False

        flexible = self.flexible_hours_check.isChecked()

        if flexible:
            hours = self.hours_spinbox.value()

            if hours <= 0:
                QMessageBox.warning(self,"Invalid Hours","Flexible hours must be greater than 0.")
                self.hours_spinbox.setFocus()
                return False

        else:
            start = self.start_time_edit.time()
            end = self.end_time_edit.time()

            if end <= start:
                QMessageBox.warning(self,"Invalid Time","The end time must be after the start time.")
                self.end_time_edit.setFocus()
                return False

        return True


    def save_shift(self):

        if not self.validate():
            return

        name = self.shift_name_edit.text().strip()
        day = self.day_combo.currentIndex()
        flexible = self.flexible_hours_check.isChecked()
        rate = self.rate_spinbox.value()

        if flexible:
            start_time = None
            end_time = None
            hours = self.hours_spinbox.value()

        else:
            start_time = self.start_time_edit.time().toString("HH:mm")
            end_time = self.end_time_edit.time().toString("HH:mm")
            hours = self.hours_spinbox.value()

        shift = Shift(
            day_of_week=day,
            start_time=start_time,
            end_time=end_time,
            hours=hours,
            location=name,
            rate=rate,
            shift_id=self.shift.id if self.edit_mode else None
        )

        self.saved.emit(shift)
        self.accept()

    def delete_shift(self):
        if not self.edit_mode or self.shift is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Shift",
            f"Are you sure you want to delete "
            f"'{self.shift.location}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.deleted.emit(self.shift)
        self.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.done(QDialog.Rejected)
            event.accept()
            return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.save_shift()
            return

        if event.key() == Qt.Key_Escape:
            self.cancel
            event.accept()
            return

        super().keyPressEvent(event)

    def cancel(self):
        self.done(QDialog.Rejected)

    def eventFilter(self, obj, event):
        if obj == self.ui and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.done(QDialog.Rejected)
                event.accept()
                return True

        return super().eventFilter(obj, event)
