from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QApplication, QMessageBox

from ui.home_page import HomePage
from ui.select_template import SelectTemplatePage
from ui.select_date import SelectDatePage
from ui.holiday_overview import HolidayOverviewPage
from ui.schedule_preview import SchedulePreviewPage
from ui.manage_templates import ManageTemplatesPage
from ui.manage_holidays import ManageHolidaysPage
from ui.template_editor import TemplateEditorPage
from ui.saved_schedules_page import SavedSchedulesPage

from models.template import EmployeeTemplate

from services.schedule_generator import ScheduleGenerator


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
        self.schedule_preview_origin = None

         # Create application pages
        self.home_page = HomePage()
        self.select_template_page = SelectTemplatePage(self.database)
        self.select_date_page = SelectDatePage()
        self.holiday_overview_page = HolidayOverviewPage()
        self.schedule_preview_page = SchedulePreviewPage()
        self.schedule_generator = ScheduleGenerator()
        self.manage_templates_page = ManageTemplatesPage(self.database)
        self.manage_holidays_page = ManageHolidaysPage(self.database)
        self.template_editor_page = TemplateEditorPage(self.database)
        self.saved_schedules_page = SavedSchedulesPage(self.database)

        # Add pages to the application stack
        self.page_stack.addWidget(self.home_page)
        self.page_stack.addWidget(self.select_template_page)
        self.page_stack.addWidget(self.select_date_page)
        self.page_stack.addWidget(self.holiday_overview_page)
        self.page_stack.addWidget(self.schedule_preview_page)
        self.page_stack.addWidget(self.manage_templates_page)
        self.page_stack.addWidget(self.manage_holidays_page)
        self.page_stack.addWidget(self.template_editor_page)
        self.page_stack.addWidget(self.saved_schedules_page)

        # Connect page signals to navigation
        self.home_page.generate_schedule_clicked.connect(self.show_select_template)
        self.home_page.saved_schedule_clicked.connect(self.show_saved_schedules)
        self.home_page.manage_templates_clicked.connect(self.show_manage_templates)
        self.home_page.manage_holidays_clicked.connect(self.show_manage_holidays)
        self.select_template_page.continue_clicked.connect(self.template_selected)
        self.select_date_page.continue_clicked.connect(self.dates_selected)
        self.saved_schedules_page.select_requested.connect(self.load_saved_schedule)
        self.manage_templates_page.add_template_clicked.connect(self.show_add_new_template)
        self.manage_templates_page.edit_template_clicked.connect(self.show_edit_template)

        # Back buttons
        self.select_template_page.back_clicked.connect(self.show_home)
        self.manage_templates_page.back_clicked.connect(self.show_home)
        self.manage_holidays_page.back_clicked.connect(self.show_home)
        self.select_date_page.back_clicked.connect(self.show_select_template)
        self.holiday_overview_page.back_clicked.connect(self.show_select_dates)
        self.schedule_preview_page.back_clicked.connect(self.schedule_preview_back)
        self.saved_schedules_page.back_requested.connect(self.show_home)
        self.template_editor_page.back_clicked.connect(self.show_manage_templates)

        # Save Template
        self.template_editor_page.saved.connect(self.template_saved)

        # Save Schedule
        self.schedule_preview_page.save_requested.connect(self.save_schedule)

        # Exit button
        self.home_page.exit_clicked.connect(self.close_application)

        # Start on Home
        self.show_home()

    def show_home(self):
        self.page_stack.setCurrentWidget(self.home_page)

    def show_select_template(self):
        self.select_template_page.load_templates()
        self.page_stack.setCurrentWidget(self.select_template_page)

    def show_saved_schedules(self):
        self.saved_schedules_page.load_saved_schedules()
        self.page_stack.setCurrentWidget(self.saved_schedules_page)

    def show_manage_templates(self):
        self.page_stack.setCurrentWidget(self.manage_templates_page)

    def show_manage_holidays(self):
        self.manage_holidays_page.load_employees()
        self.manage_holidays_page.load_holidays()
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
        template = self.selected_template
        schedule = self.schedule_generator.generate(
            template,
            start_date,
            end_date
        )

        self.schedule_preview_page.set_schedule(schedule)
        self.schedule_preview_page.show_first_week()
        self.schedule_preview_origin = "select_dates"
        self.show_schedule_preview()

    def show_schedule_preview(self):
        self.page_stack.setCurrentWidget(
            self.schedule_preview_page
        )

    def save_schedule(self):
        schedule = self.schedule_preview_page.schedule

        if schedule is None:
            return

        schedule_id = self.database.save_schedule(schedule)

        QMessageBox.information(
            self,
            "Schedule Saved",
            f"{schedule.template.name}'s schedule has been saved successfully."
        )

    def load_saved_schedule(self, schedule_id):
        schedule = self.database.load_schedule(schedule_id)
        if schedule is None:
            return

        self.schedule_preview_page.set_schedule(schedule)
        self.schedule_preview_page.show_first_week()
        self.schedule_preview_origin = "saved_schedules"
        self.show_schedule_preview()

    def schedule_preview_back(self):
        if self.schedule_preview_origin == "saved_schedules":
            self.show_saved_schedules()

        else:
            self.show_select_dates()

    def close_application(self):
        QApplication.quit()
