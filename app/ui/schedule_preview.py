from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget,QVBoxLayout,QPushButton,QLayout,QFrame,QHBoxLayout,QLabel,QSizePolicy, QApplication, QFileDialog, QMessageBox


from ui.week_preview import WeekPreview
from ui.schedule_header import ScheduleHeader
from ui.preview_page import PreviewPage

from services.schedule_pdf_exporter import SchedulePdfExporter


class SchedulePreviewPage(QWidget):

    back_clicked = Signal()
    save_requested = Signal()

    def __init__(self):
        super().__init__()
        self.schedule = None
        loader = QUiLoader()
        self.ui = loader.load("ui_files/schedule_preview.ui",None)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.ui)

        self.back_button = self.ui.findChild(QPushButton,"back_button")
        self.save_button = self.ui.findChild(QPushButton,"save_button")
        self.export_pdf_button = self.ui.findChild(QPushButton,"export_pdf_button")
        self.preview_content_layout = self.ui.findChild(QLayout,"preview_layout")
        self.preview_content = self.ui.findChild(QWidget,"preview_content")
        self.preview_content_layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.preview_content.setMinimumWidth(1060)
        self.preview_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.preview_pages = []

        self.back_button.clicked.connect(self.back_clicked.emit)
        self.ui.save_button.clicked.connect(self.save_requested.emit)
        self.export_pdf_button.clicked.connect(self.export_pdf)

    def set_schedule(self, schedule):
        self.schedule = schedule

    def show_first_week(self):
        if self.schedule is None:
            return
        QTimer.singleShot(0, self._render_preview)

    def _render_preview(self):
        self.clear_preview()
        QApplication.processEvents()
        self.ui.preview_scroll_area.verticalScrollBar().setValue(0)
        self.ui.preview_scroll_area.horizontalScrollBar().setValue(0)
        weeks = []

        for i in range(0, len(self.schedule.days), 7):
            week_days = self.schedule.days[i:i + 7]
            week_widget = WeekPreview(
                week_days,
                self.schedule.start_date,
                self.schedule.end_date
            )
            week_widget.adjustSize()
            weeks.append(week_widget)

        current_page = None
        current_height = 0

        for week_widget in weeks:
            if current_page is None:
                current_page = self.create_preview_page()
                header = ScheduleHeader(self.schedule)
                current_page.page_layout.addWidget(header,alignment=Qt.AlignTop)
                current_height = header.sizeHint().height()

            week_height = week_widget.sizeHint().height()
            spacing = current_page.page_layout.spacing()
            required_height = (current_height + spacing + week_height)

            if required_height > current_page.available_height:
                current_page = self.create_preview_page()
                header = ScheduleHeader(self.schedule)
                current_page.page_layout.addWidget(header,alignment=Qt.AlignTop)
                current_height = header.sizeHint().height()
                required_height = (current_height + current_page.page_layout.spacing() + week_height)

            current_page.page_layout.addWidget(week_widget,alignment=Qt.AlignTop)
            current_height = (current_height + current_page.page_layout.spacing() + week_height)

        period_summary = self.create_period_summary()
        current_page.page_layout.addWidget(period_summary,alignment=Qt.AlignTop)
        QTimer.singleShot(0, self._finalize_preview)


    def create_period_summary(self):
        summary = QFrame()
        summary.setObjectName("period_summary")
        summary_layout = QHBoxLayout(summary)
        summary_layout.setContentsMargins(10,5,10,5)
        summary_layout.setSpacing(16)
        summary.setFixedHeight(30)
        title_label = QLabel("Period Total")
        title_label.setStyleSheet("""
            QLabel {
                color: #52636F;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        hours_label = QLabel(self.format_hours(self.schedule.total_hours))
        pay_label = QLabel(f"£{self.schedule.total_pay:.2f}")

        hours_label.setStyleSheet("""
            QLabel {
                color: #263238;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        pay_label.setStyleSheet("""
            QLabel {
                color: #263238;
                font-size: 12px;
                font-weight: 600;
            }
        """)

        summary_layout.addStretch()
        summary_layout.addWidget(title_label)
        summary_layout.addWidget(hours_label)
        summary_layout.addWidget(pay_label)

        summary.setStyleSheet("""
            #period_summary {
                background-color: #E9EEF1;
                border: 1px solid #C7D0D6;
                border-radius: 7px;
            }
        """)

        return summary

    def create_preview_page(self):
        page = PreviewPage()
        self.preview_pages.append(page)
        self.preview_content_layout.addWidget(
            page,
            alignment=Qt.AlignHCenter | Qt.AlignTop
        )

        return page

    def clear_preview(self):
        while self.preview_content_layout.count():

            item = self.preview_content_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        self.preview_pages.clear()

        self.preview_content_layout.invalidate()
        self.preview_content_layout.activate()

        self.preview_content.setMinimumSize(0, 0)
        self.preview_content.resize(
            self.ui.preview_scroll_area.viewport().width(),
            self.ui.preview_scroll_area.viewport().height()
        )
        self.ui.preview_scroll_area.verticalScrollBar().setValue(0)
        self.ui.preview_scroll_area.horizontalScrollBar().setValue(0)

    def _finalize_preview(self):
        self.preview_content_layout.invalidate()
        self.preview_content_layout.activate()
        content_size = self.preview_content_layout.sizeHint()
        scroll_area_width = self.ui.preview_scroll_area.width()
        content_width = max(scroll_area_width,content_size.width())
        content_height = content_size.height()
        self.preview_content.resize(content_width,content_height)
        self.preview_content_layout.setGeometry(self.preview_content.rect())

    def export_pdf(self):
        if self.schedule is None:
            return

        default_name = (
            f"{self.schedule.template.name} "
            f"{self.schedule.start_date.toString('dd_MM')} - "
            f"{self.schedule.end_date.toString('dd_MM')}.pdf"
        )

        file_path, _ = QFileDialog.getSaveFileName(self,"Export Schedule as PDF",default_name,"PDF Files (*.pdf)")

        # User cancelled the save dialog
        if not file_path:
            return
        try:
            exporter = SchedulePdfExporter()
            exporter.export(self.schedule,file_path)
        except Exception as e:
            QMessageBox.critical(self,"PDF Export Failed",f"Could not create the PDF.\n\n{e}")
            return
        QMessageBox.information(self,"PDF Exported",f"Schedule exported successfully.\n\n"f"Saved to:\n{file_path}")


    @staticmethod
    def format_hours(hours):

        if hours.is_integer():
            return f"{int(hours)} hours"

        return f"{hours:g} hours"