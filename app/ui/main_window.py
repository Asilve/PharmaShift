from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QApplication

from ui.home_page import HomePage
from ui.generate_schedule import GenerateSchedulePage
from ui.manage_templates import ManageTemplatesPage
from ui.manage_holidays import ManageHolidaysPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pharma Shift")
        self.setFixedSize(1280,720)

        loader = QUiLoader()
        self.ui = loader.load("ui_files/main_window.ui")

        self.setCentralWidget(self.ui)

        self.page_stack = self.ui.findChild(QStackedWidget, "page_stack")

         # Create application pages
        self.home_page = HomePage()
        self.generate_schedule_page = GenerateSchedulePage()
        self.manage_templates_page = ManageTemplatesPage()
        self.manage_holidays_page = ManageHolidaysPage()

        # Add pages to the application stack
        self.page_stack.addWidget(self.home_page)
        self.page_stack.addWidget(self.generate_schedule_page)
        self.page_stack.addWidget(self.manage_templates_page)
        self.page_stack.addWidget(self.manage_holidays_page)

        # Connect page signals to navigation
        self.home_page.generate_schedule_clicked.connect(self.show_generate_schedule)
        self.home_page.manage_templates_clicked.connect(self.show_manage_templates)
        self.home_page.manage_holidays_clicked.connect(self.show_manage_holidays)

        # Back to home buttons
        self.generate_schedule_page.back_clicked.connect(self.show_home)
        self.manage_templates_page.back_clicked.connect(self.show_home)
        self.manage_holidays_page.back_clicked.connect(self.show_home)

        # Exit button
        self.home_page.exit_clicked.connect(self.close_application)

        # Start on Home
        self.show_home()

    def show_home(self):
        self.page_stack.setCurrentWidget(self.home_page)

    def show_generate_schedule(self):
        self.page_stack.setCurrentWidget(self.generate_schedule_page)

    def show_manage_templates(self):
        self.page_stack.setCurrentWidget(self.manage_templates_page)

    def show_manage_holidays(self):
        self.page_stack.setCurrentWidget(self.manage_holidays_page)

    def close_application(self):
        QApplication.quit()