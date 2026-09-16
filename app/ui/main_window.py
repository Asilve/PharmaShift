from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QApplication

from ui.home_page import HomePage
from ui.select_template import SelectTemplatePage
from ui.select_date import SelectDatePage
from ui.holiday_overview import HolidayOverviewPage
from ui.manage_templates import ManageTemplatesPage
from ui.manage_holidays import ManageHolidaysPage
from ui.template_editor import TemplateEditorPage
from models.template import EmployeeTemplate



class MainWindow(QMainWindow):
    def __init__(self, database):
        super().__init__()

        self.database = database

        self.setWindowTitle("Pharma Shift")
        self.setFixedSize(1280,720)

        loader = QUiLoader()
        self.ui = loader.load("ui_files/main_window.ui")

        self.setCentralWidget(self.ui)

        self.page_stack = self.ui.findChild(QStackedWidget, "page_stack")

        # Schedule generation state
        self.selected_template = None
        self.start_date = None
        self.end_date = None

         # Create application pages
        self.home_page = HomePage()
        self.select_template_page = SelectTemplatePage(self.database)
        self.select_date_page = SelectDatePage()
        self.holiday_overview_page = HolidayOverviewPage()
        self.manage_templates_page = ManageTemplatesPage(self.database)
        self.manage_holidays_page = ManageHolidaysPage()
        self.template_editor_page = TemplateEditorPage(self.database)

        # Add pages to the application stack
        self.page_stack.addWidget(self.home_page)
        self.page_stack.addWidget(self.select_template_page)
        self.page_stack.addWidget(self.select_date_page)
        self.page_stack.addWidget(self.holiday_overview_page)
        self.page_stack.addWidget(self.manage_templates_page)
        self.page_stack.addWidget(self.manage_holidays_page)
        self.page_stack.addWidget(self.template_editor_page)

        # Connect page signals to navigation
        self.home_page.generate_schedule_clicked.connect(self.show_select_template)
        self.home_page.manage_templates_clicked.connect(self.show_manage_templates)
        self.home_page.manage_holidays_clicked.connect(self.show_manage_holidays)
        self.select_template_page.continue_clicked.connect(self.template_selected)
        self.select_date_page.continue_clicked.connect(self.dates_selected)
        self.manage_templates_page.add_template_clicked.connect(self.show_add_new_template)
        self.manage_templates_page.edit_template_clicked.connect(self.show_edit_template)

        # Back buttons
        self.select_template_page.back_clicked.connect(self.show_home)
        self.manage_templates_page.back_clicked.connect(self.show_home)
        self.manage_holidays_page.back_clicked.connect(self.show_home)
        self.select_date_page.back_clicked.connect(self.show_select_template)
        self.holiday_overview_page.back_clicked.connect(self.show_select_dates)
        self.template_editor_page.back_clicked.connect(self.show_manage_templates)

        # Save Template
        self.template_editor_page.saved.connect(self.template_saved)

        # Exit button
        self.home_page.exit_clicked.connect(self.close_application)

        # Start on Home
        self.show_home()

    def show_home(self):
        self.page_stack.setCurrentWidget(self.home_page)

    def show_select_template(self):
        self.select_template_page.load_templates()
        self.page_stack.setCurrentWidget(self.select_template_page)

    def show_manage_templates(self):
        self.page_stack.setCurrentWidget(self.manage_templates_page)

    def show_manage_holidays(self):
        self.page_stack.setCurrentWidget(self.manage_holidays_page)

    def show_select_dates(self):
        self.page_stack.setCurrentWidget(self.select_date_page)

    def show_holiday_overview(self):
        self.page_stack.setCurrentWidget(self.holiday_overview_page)
    
    def show_add_new_template(self):
        template = EmployeeTemplate(name="",colour="#FFFFFF",notes="")
        self.template_editor_page.set_template(template)
        self.page_stack.setCurrentWidget(self.template_editor_page)

    def show_edit_template(self, template):
        full_template = self.database.get_template(template.id)

        if full_template is None:
            return    
        self.template_editor_page.set_template(full_template)
        self.page_stack.setCurrentWidget(self.template_editor_page)

    def template_saved(self):
        self.manage_templates_page.load_templates()
        self.show_manage_templates()

    def template_selected(self, template):
        self.selected_template = template
        self.show_select_dates()

    def dates_selected(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.show_holiday_overview()

    def close_application(self):
        QApplication.quit()
