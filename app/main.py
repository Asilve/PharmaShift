import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile


def main():
    app = QApplication(sys.argv)

    loader = QUiLoader()
    window = loader.load("ui_files/home.ui", None)

    window.setWindowTitle("Pharma Shift")
    window.resize(1280, 720)

    window.show()
    sys.exit(app.exec())


main()