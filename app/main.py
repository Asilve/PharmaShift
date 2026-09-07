import sys

from PySide6.QtWidgets import QApplication, QMainWindow


def main():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Pharma-Shift")
    window.resize(1200, 700)

    window.show()

    sys.exit(app.exec())


main()