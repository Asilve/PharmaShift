import sys
import resources_rc
from database.database import Database

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

from PySide6.QtCore import QDate
from services.schedule_pdf_exporter import SchedulePdfExporter


def main():
    app = QApplication(sys.argv)

    database = Database()
    database.create_tables()

    window = MainWindow(database)
    window.show()

    sys.exit(app.exec())


main()