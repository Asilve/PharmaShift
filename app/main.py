import sys, os
import resources_rc
from database.database import Database

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)

    return os.path.join(
        os.path.abspath("."),
        relative_path
    )

def main():
    if hasattr(sys, "_MEIPASS"):
        os.chdir(sys._MEIPASS)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/assets/logo.png"))

    database = Database(os.path.join(os.path.dirname(sys.executable), "PharmaShift.db"))
    database.create_tables()

    window = MainWindow(database)
    window.show()

    sys.exit(app.exec())


main()