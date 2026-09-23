from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


class SchedulePdfExporter:

    def __init__(self):
        self.width, self.height = landscape(A4)

        # Page
        self.margin = 40

        # These correspond to the structure of the Schedule Preview.
        self.day_header_height = 34
        self.day_summary_height = 32

        self.shift_padding = 5
        self.shift_spacing = 4

        self.weekly_summary_height = 28
        self.week_spacing = 8

        self.header_height = 45


    def export(self, schedule, file_path):
        pdf = canvas.Canvas(file_path,landscape(A4))

        weeks = [schedule.days[i:i + 7] for i in range(0, len(schedule.days), 7)]
        current_y = self.height - self.margin
        self.draw_header(pdf,schedule,current_y)

        current_y -= self.header_height

        for week_days in weeks:
            week_height = self.calculate_week_height(week_days,schedule)

            # Start a new page if this week does not fit.
            if current_y - week_height < self.margin:
                pdf.showPage()
                current_y = self.height - self.margin
                self.draw_header(pdf,schedule,current_y)
                current_y -= self.header_height

            self.draw_week(pdf,week_days,schedule,current_y,week_height)

            current_y -= week_height
            current_y -= self.week_spacing

        # Period total
        period_summary_height = 30
        if current_y - period_summary_height >= self.margin:
            self.draw_period_summary(pdf,schedule,self.margin,current_y - period_summary_height,self.width - (self.margin * 2))

        else:
            pdf.showPage()
            current_y = self.height - self.margin
            self.draw_header(pdf,schedule,current_y)
            current_y -= self.header_height
            self.draw_period_summary(pdf,schedule,self.margin,current_y - period_summary_height,self.width - (self.margin * 2))
        pdf.save()

    # Header
    def draw_header(self, pdf, schedule, y):
        # Employee / template name
        pdf.setFont("Helvetica-Bold",12)
        pdf.drawString(self.margin,y,schedule.template.name)

        # Employee note
        if schedule.template.notes:
            pdf.setFont("Helvetica",8)
            pdf.drawString(self.margin,y - 14,schedule.template.notes)

        # Date range on the right
        pdf.setFont("Helvetica",8)
        date_range = (f"{schedule.start_date.toString('dd/MM/yyyy')} - " f"{schedule.end_date.toString('dd/MM/yyyy')}")

        pdf.drawRightString(
            self.width - self.margin,y - 4,date_range)

        # Divider
        pdf.line(self.margin,y - 28,self.width - self.margin,y - 28)

    # Week sizing
    def calculate_week_height(self,week_days,schedule):
        tallest_day = 0
        for day in week_days:
            day_height = self.calculate_day_height(day,schedule)
            tallest_day = max(tallest_day,day_height)

        return (tallest_day+ self.weekly_summary_height)

    def calculate_day_height(self,day,schedule):
        # Days outside the requested period use the
        # smaller/empty presentation.
        in_period = (schedule.start_date <= day.date <= schedule.end_date)

        if not in_period:
            return 38 + 50
        
        # Header
        height = self.day_header_height

        # Shift area
        if day.shifts:
            shift_height = 0
            for shift in day.shifts:
                shift_height += self.calculate_shift_height(shift)

            # Shift area padding + spacing between shifts
            shift_height += (self.shift_padding * 2)

            if len(day.shifts) > 1:
                shift_height += (self.shift_spacing * (len(day.shifts) - 1))
            height += shift_height

        else:
            # Empty shift area still exists.
            height += (self.shift_padding * 2)

        # Day summary
        height += self.day_summary_height
        return height

    def calculate_shift_height(self, shift):
        # Location
        height = 12

        # Timed shifts have an additional line.
        if (shift.start_time is not None and shift.end_time is not None):
            height += 10

        # Hours + rate
        height += 10

        # Total pay
        height += 12

        # Frame padding
        height += 6

        return height

    # Week rendering
    def draw_week(self,pdf,week_days,schedule,top_y,week_height):
        usable_width = (self.width- (self.margin * 2))
        day_width = (usable_width / 7)
        day_height = (week_height - self.weekly_summary_height)

        for index, day in enumerate(week_days):
            x = (self.margin + (index * day_width))
            self.draw_day_box(pdf,day,schedule,x,top_y - day_height,day_width,day_height)

        # Weekly total
        summary_y = (top_y- day_height- self.weekly_summary_height)

        self.draw_weekly_summary(pdf,week_days,x=self.margin,y=summary_y,width=usable_width)

    # Day
    def draw_day_box(self,pdf,day,schedule,x,y,width,height):
        in_period = (schedule.start_date<= day.date<= schedule.end_date)

        # Outer day box
        pdf.rect(x,y,width,height)

        # Day header
        header_y = (y+ height- self.day_header_height)
        pdf.rect(x,header_y,width,self.day_header_height)
        pdf.setFont("Helvetica-Bold",7)
        day_name = day.date.toString("ddd").upper()
        pdf.drawCentredString(x + (width / 2),header_y + 21,day_name)

        pdf.setFont("Helvetica-Bold",9)
        date_text = day.date.toString("d MMM")
        pdf.drawCentredString(x + (width / 2),header_y + 8,date_text)

        # Outside-period days stop here.
        if not in_period:
            return

        # Shifts
        shift_y = (header_y - self.shift_padding)

        for shift in day.shifts:
            shift_height = (self.calculate_shift_height(shift))
            shift_y -= shift_height
            self.draw_shift(pdf,shift,x + self.shift_padding,shift_y,width - (self.shift_padding * 2),shift_height)
            shift_y -= self.shift_spacing

        # Day summary
        summary_y = y
        pdf.rect(x,summary_y,width,self.day_summary_height)
        pdf.setFont("Helvetica-Bold",8)

        if day.shifts:
            hours_text = self.format_hours(day.total_hours)
            pay_text = (f"£{day.total_pay:.2f}")
            pdf.drawCentredString(x + (width / 2),summary_y + 21,hours_text)

            pdf.setFont("Helvetica",7)
            pdf.drawCentredString(x + (width / 2),summary_y + 9,pay_text)

        else:
            pdf.setFont("Helvetica",7)
            pdf.drawCentredString(x + (width / 2),summary_y + 13,"---")

    # Shift
    def draw_shift(self,pdf,shift,x,y,width,height):
        pdf.roundRect(x,y,width,height,5)

        text_x = x + 4
        current_y = (y+ height- 13)

        # Location
        pdf.setFont("Helvetica-Bold",7)
        pdf.drawString(text_x,current_y,shift.location)
        current_y -= 11

        # Timed shift
        if (shift.start_time is not None and shift.end_time is not None):
            pdf.setFont("Helvetica",6)
            pdf.drawString(text_x,current_y,f"{shift.start_time} - " f"{shift.end_time}")
            current_y -= 11

        # Hours
        pdf.setFont("Helvetica",6)
        pdf.drawString(text_x,current_y,self.format_hours(shift.hours))

        # Rate
        pdf.drawRightString(x + width - 4,current_y,f"£{shift.rate:.2f}/hr")
        current_y -= 12

        # Total
        pdf.setFont("Helvetica-Bold",7)
        total_pay = (shift.hours* shift.rate)
        pdf.drawRightString(x + width - 4,current_y,f"Total: £{total_pay:.2f}")

    # Weekly total
    def draw_weekly_summary(self,pdf,week_days,x,y,width):
        total_hours = sum(day.total_hours for day in week_days)
        total_pay = sum(day.total_pay for day in week_days)

        pdf.rect(x,y,width,self.weekly_summary_height)
        pdf.setFont("Helvetica-Bold",8)

        text = (f"Weekly Total   "f"{self.format_hours(total_hours)}   " f"£{total_pay:.2f}")
        pdf.drawRightString(x + width - 10,y + 10,text)

    # Helpers
    @staticmethod
    def format_hours(hours):
        if hours is None:
            return "0 hours"

        if hours.is_integer():
            return f"{int(hours)} hours"

        return f"{hours:g} hours"


    def draw_period_summary(self,pdf,schedule,x,y,width):
        pdf.rect(x,y,width,30)
        pdf.setFont("Helvetica-Bold",9)

        text = (f"Period Total   "f"{self.format_hours(schedule.total_hours)}   "f"£{schedule.total_pay:.2f}")
        pdf.drawRightString(x + width - 10,y + 10,text)