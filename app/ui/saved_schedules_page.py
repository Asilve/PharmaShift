from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLayout, QSizePolicy, QMessageBox
from PySide6.QtCore import Signal, Qt, QEvent

from ui.saved_schedule_card import SavedScheduleCard


class SavedSchedulesPage(QWidget):

    back_requested = Signal()
    select_requested = Signal(int)

    def __init__(self, database):
        super().__init__()

        self.database = database

        loader = QUiLoader()
        self.ui = loader.load("ui_files/saved_schedules.ui")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.installEventFilter(self)
        self.ui.installEventFilter(self)
        self.ui.scrollArea.viewport().installEventFilter(self)

        self.selected_schedule_id = None
        self.cards = []

        self.back_button = self.ui.findChild(QPushButton, "back_button")
        self.back_button.clicked.connect(self.back_requested.emit)

        self.card_layout = self.ui.findChild(QLayout,"card_layout")

        self.card_layout.setAlignment(Qt.AlignTop)
        self.card_layout.setSpacing(6)
        self.card_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        self.ui.scrollArea.setWidgetResizable(True)

        self.ui.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_content = self.ui.findChild(QWidget,"scroll_content")
        self.scroll_content.setMinimumHeight(0)
        self.scroll_content.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)

        self.delete_button = self.ui.findChild(QPushButton, "delete_button")
        self.select_button = self.ui.findChild(QPushButton, "select_button")
        self.select_button.setEnabled(False)
        self.delete_button.setEnabled(False)

        self.delete_button.clicked.connect(self.delete_selected_schedule)
        self.select_button.clicked.connect(self.select_saved_schedule)

        self.load_saved_schedules()

    def load_saved_schedules(self):
        self.clear_cards()

        saved_schedules = self.database.get_saved_schedules()

        for saved_schedule in saved_schedules:
            card = SavedScheduleCard(saved_schedule)
            card.clicked.connect(lambda card=card: self.select_card(card))
            self.cards.append(card)
            self.card_layout.addWidget(card,0,Qt.AlignHCenter | Qt.AlignTop)
            self.card_layout.invalidate()

        self.card_layout.activate()
        self.scroll_content.setMinimumHeight(self.card_layout.sizeHint().height())
        self.clear_selection()

    def clear_cards(self):
        while self.card_layout.count():
            item = self.card_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.cards.clear()

    def select_card(self, selected_card):
        for card in self.cards:
            card.set_selected(card is selected_card)

        self.selected_schedule_id = selected_card.saved_schedule[0]

        self.select_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def delete_selected_schedule(self):
        if self.selected_schedule_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Schedule",
            "Are you sure you want to delete this saved schedule?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.database.delete_schedule(self.selected_schedule_id)

        self.load_saved_schedules()

    def select_saved_schedule(self):
        if self.selected_schedule_id is None:
            return

        self.select_requested.emit(self.selected_schedule_id)

    def clear_selection(self):
        for card in self.cards:
            card.set_selected(False)

        self.selected_schedule_id = None

        self.select_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def mousePressEvent(self, event):
        self.clear_selection()
        super().mousePressEvent(event)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            if watched == self.ui.scrollArea.viewport():
                self.clear_selection()

        return super().eventFilter(watched, event)
