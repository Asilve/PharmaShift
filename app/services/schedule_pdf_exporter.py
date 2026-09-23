from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor


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
        self.header_week_spacing = 8

        self.outside_day_summary_height = 50

        # Colours - match Schedule Preview
        self.primary_text = "#263238"
        self.secondary_text = "#52636F"
        self.muted_text = "#71808A"
        self.placeholder_text = "#9AA4AB"

        self.day_border = "#D7DEE5"

        self.shift_background = "#F4F7FA"
        self.shift_border = "#BFC9D1"

        self.weekly_background = "#F4F7FA"
        self.weekly_border = "#D7DEE5"

        self.period_background = "#E9EEF1"
        self.period_border = "#C7D0D6"

        self.outside_background = "#F5F5F5"
        self.outside_border = "#E1E1E1"
        self.outside_text = "#B0B7BC"


    def export(self, schedule, file_path):
        pdf = canvas.Canvas(file_path,landscape(A4))

        weeks = [schedule.days[i:i + 7] for i in range(0, len(schedule.days), 7)]
        current_y = self.height - self.margin
        self.draw_header(pdf,schedule,current_y)

        current_y -= (self.header_height + self.header_week_spacing)

        for week_days in weeks:
            week_height = self.calculate_week_height(week_days,schedule)

            # Start a new page if this week does not fit.
            if current_y - week_height < self.margin:
                pdf.showPage()
                current_y = self.height - self.margin
                self.draw_header(pdf,schedule,current_y)
                current_y -= (self.header_height + self.header_week_spacing)

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
        # Header dimensions
        header_x = self.margin
        header_y = y - self.header_height
        header_width = (self.width - (self.margin * 2))
        header_height = self.header_height

        # Header card
        pdf.setFillColor(self.color("#FFFFFF"))
        pdf.setStrokeColor(self.color(self.day_border))
        pdf.setLineWidth(1)
        pdf.roundRect(header_x,header_y,header_width,header_height,7,fill=1,stroke=1)

        # Colour bar
        colour_bar_width = 5
        colour_bar_height = 30
        colour_bar_x = (header_x + 8)
        colour_bar_y = (header_y+ ((header_height - colour_bar_height) / 2))

        pdf.setFillColor(self.color(schedule.template.colour))
        pdf.roundRect(colour_bar_x,colour_bar_y,colour_bar_width,colour_bar_height,2.5,fill=1,stroke=0)

        # Employee / template name
        text_x = (colour_bar_x+ colour_bar_width+ 8)
        name_y = (header_y+ header_height- 18)
        pdf.setFillColor(self.color(self.primary_text))
        pdf.setFont("Helvetica-Bold",14)
        pdf.drawString(text_x,name_y,schedule.template.name)

        # Notes
        if schedule.template.notes:
            pdf.setFillColor(self.color(self.muted_text))
            pdf.setFont("Helvetica",8)
            pdf.drawString(text_x,header_y + 11,schedule.template.notes)

        # Date range
        date_range = (f"{schedule.start_date.toString('d MMM yyyy')} - " f"{schedule.end_date.toString('d MMM yyyy')}")
        pdf.setFillColor(self.color(self.secondary_text))
        pdf.setFont("Helvetica-Bold",9)
        pdf.drawRightString(header_x + header_width - 8,header_y + 19,date_range)

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
            return (self.day_header_height + self.outside_day_summary_height)
        
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
        usable_width = (self.width - (self.margin * 2))
        day_width = (usable_width / 7)
        day_height = (week_height- self.weekly_summary_height)

        # Draw all day boxes first
        for index, day in enumerate(week_days):
            x = (self.margin+ (index * day_width))
            self.draw_day_box(pdf,day,schedule,x,top_y - day_height,day_width,day_height)

        body_top = top_y - self.day_header_height
        body_bottom = (top_y- day_height+ self.day_summary_height)
        pdf.setStrokeColor(self.color(self.day_border))
        pdf.setLineWidth(1)

        # Left edge
        pdf.line(self.margin,body_bottom,self.margin,body_top)

        # Internal separators
        for index in range(1, 7):
            x = (self.margin+ (index * day_width))
            pdf.line(x,body_bottom,x,body_top)

        # Right edge
        pdf.line(self.margin + usable_width,body_bottom,self.margin + usable_width,body_top)

        # Weekly total
        summary_y = (top_y- day_height- self.weekly_summary_height)
        self.draw_weekly_summary(pdf,week_days,x=self.margin,y=summary_y,width=usable_width)

    # Day
    def draw_day_box(self,pdf,day,schedule,x,y,width,height):
        in_period = (schedule.start_date<= day.date<= schedule.end_date)

        # Header position
        header_y = (y+ height- self.day_header_height)

        # Outside-period day
        if not in_period:

            # Header
            pdf.setFillColor(self.color(self.outside_background))
            pdf.setStrokeColor(self.color(self.outside_border))
            pdf.setLineWidth(1)
            pdf.rect(x,header_y,width,self.day_header_height,fill=1,stroke=1)

            # Day name
            pdf.setFillColor(self.color(self.outside_text))
            pdf.setFont("Helvetica-Bold",7)
            day_name = day.date.toString("ddd").upper()

            pdf.drawCentredString(x + (width / 2),header_y + 21,day_name)

            # Date
            pdf.setFont("Helvetica-Bold",9)
            date_text = day.date.toString("d MMM")
            pdf.drawCentredString(x + (width / 2),header_y + 8,date_text)

            # Empty body
            body_y = (y+ self.outside_day_summary_height)
            body_height = (height- self.day_header_height- self.outside_day_summary_height)
            pdf.setFillColor(self.color(self.outside_background))
            pdf.setStrokeColor(self.color(self.outside_border))
            pdf.rect(x,body_y,width,body_height,fill=1,stroke=1)

            # Empty summary
            summary_y = y

            pdf.rect(x,summary_y,width,self.outside_day_summary_height,fill=1,stroke=1)

            return

        # Normal day

        # White day header
        pdf.setFillColor(self.color("#FFFFFF"))
        pdf.setStrokeColor(self.color(self.day_border))
        pdf.setLineWidth(1)
        pdf.rect(x,header_y,width,self.day_header_height,fill=1,stroke=1)

        # Day name
        pdf.setFillColor(self.color(self.secondary_text))
        pdf.setFont("Helvetica-Bold",7)
        day_name = day.date.toString("ddd").upper()

        pdf.drawCentredString(x + (width / 2),header_y + 21,day_name)

        # Date
        pdf.setFillColor(self.color(self.primary_text))
        pdf.setFont("Helvetica-Bold",9)
        date_text = day.date.toString("d MMM")
        pdf.drawCentredString(x + (width / 2),header_y + 8,date_text)

        # Shift area
        # Body background + vertical borders
        body_y = (y+ self.day_summary_height)
        body_height = (height- self.day_header_height- self.day_summary_height)
        pdf.setFillColor(self.color("#FFFFFF"))
        pdf.setStrokeColor(self.color(self.day_border))
        pdf.setLineWidth(1)
        shift_area_y = (header_y- self.shift_padding)

        for shift in day.shifts:
            shift_height = (self.calculate_shift_height(shift))
            shift_area_y -= shift_height
            self.draw_shift(pdf,shift,x + self.shift_padding,shift_area_y,width - (self.shift_padding * 2),shift_height)
            shift_area_y -= self.shift_spacing

        # Day summary
        summary_y = y
        pdf.setFillColor(self.color("#FFFFFF"))
        pdf.setStrokeColor(self.color(self.day_border))
        pdf.setLineWidth(1)
        pdf.rect(x,summary_y,width,self.day_summary_height,fill=1,stroke=1)

        if day.shifts:
            # Hours
            pdf.setFillColor(self.color(self.primary_text))
            pdf.setFont("Helvetica-Bold",8)
            hours_text = self.format_hours(day.total_hours)
            pdf.drawCentredString(x + (width / 2),summary_y + 21,hours_text)

            # Pay
            pdf.setFillColor(self.color(self.muted_text))
            pdf.setFont("Helvetica",7)

            pay_text = (f"£{day.total_pay:.2f}")
            pdf.drawCentredString(x + (width / 2),summary_y + 9,pay_text)

        else:
            # Empty day
            pdf.setFillColor(self.color(self.placeholder_text))
            pdf.setFont("Helvetica",7)
            pdf.drawCentredString(x + (width / 2), summary_y + 13, "---")

    # Shift
    def draw_shift(self,pdf,shift,x,y,width,height):
        pdf.setFillColor(self.color(self.shift_background))
        pdf.setStrokeColor(self.color(self.shift_border))
        pdf.setLineWidth(1)
        pdf.roundRect(x,y,width,height,5,fill=1,stroke=1)

        text_x = x + 4
        current_y = (y+ height- 13)

        # Location
        pdf.setFillColor(self.color(self.primary_text))
        pdf.setFont("Helvetica-Bold",7)
        pdf.drawString(text_x,current_y,shift.location)
        current_y -= 11

        # Timed shift
        if (shift.start_time is not None and shift.end_time is not None):
            pdf.setFillColor(self.color(self.secondary_text))
            pdf.setFont("Helvetica",6)
            pdf.drawString(text_x,current_y,f"{shift.start_time} - " f"{shift.end_time}")
            current_y -= 11

        # Hours
        pdf.setFillColor(self.color(self.secondary_text))
        pdf.setFont("Helvetica",6)
        pdf.drawString(text_x,current_y,self.format_hours(shift.hours))

        # Rate
        pdf.drawRightString(x + width - 4,current_y,f"£{shift.rate:.2f}/hr")
        current_y -= 12

        # Total
        pdf.setFillColor(self.color(self.primary_text))
        pdf.setFont("Helvetica-Bold",7)
        total_pay = (shift.hours* shift.rate)
        pdf.drawRightString(x + width - 4,current_y,f"Total: £{total_pay:.2f}")

    # Weekly total
    def draw_weekly_summary(self,pdf,week_days,x,y,width):
        total_hours = sum(day.total_hours for day in week_days)
        total_pay = sum(day.total_pay for day in week_days)

        # Background + border
        pdf.setFillColor(self.color(self.weekly_background))
        pdf.setStrokeColor(self.color(self.weekly_border))
        pdf.setLineWidth(1)
        pdf.roundRect(x,y,width,self.weekly_summary_height,5,fill=1,stroke=1)

        # Weekly Total
        pdf.setFillColor(self.color(self.secondary_text))
        pdf.setFont("Helvetica-Bold",8)
        weekly_text = "Weekly Total"

        # Hours
        hours_text = self.format_hours(total_hours)

        # Pay
        pay_text = f"£{total_pay:.2f}"

        # Draw from right to left so the
        # three pieces stay on one line.

        right_x = x + width - 10

        pdf.setFillColor(self.color(self.primary_text))
        pdf.drawRightString(right_x,y + 10,pay_text)

        pay_width = pdf.stringWidth(pay_text,"Helvetica-Bold",8)
        right_x -= pay_width + 12
        pdf.setFillColor(self.color(self.primary_text))
        pdf.drawRightString(right_x,y + 10,hours_text)
        hours_width = pdf.stringWidth(hours_text,"Helvetica-Bold",8)
        right_x -= hours_width + 12
        pdf.setFillColor(self.color(self.secondary_text))
        pdf.drawRightString(right_x,y + 10,weekly_text)

    # Helpers
    @staticmethod
    def format_hours(hours):
        if hours is None:
            return "0 hours"

        if hours.is_integer():
            return f"{int(hours)} hours"

        return f"{hours:g} hours"


    def draw_period_summary(self,pdf,schedule,x,y,width):
        # Background + border
        pdf.setFillColor(self.color(self.period_background))
        pdf.setStrokeColor(self.color(self.period_border))
        pdf.setLineWidth(1)
        pdf.roundRect(x,y,width,30,5,fill=1,stroke=1)

        # Text values
        title_text = "Period Total"
        hours_text = self.format_hours(schedule.total_hours)
        pay_text = (f"£{schedule.total_pay:.2f}")

        # Draw from right to left
        right_x = x + width - 10

        # Pay
        pdf.setFillColor(self.color(self.primary_text))
        pdf.setFont("Helvetica-Bold",9)
        pdf.drawRightString(right_x,y + 10,pay_text)
        pay_width = pdf.stringWidth(pay_text,"Helvetica-Bold",9)

        right_x -= pay_width + 12

        # Hours
        pdf.drawRightString(right_x,y + 10,hours_text)
        hours_width = pdf.stringWidth(hours_text,"Helvetica-Bold",9)
        right_x -= hours_width + 12

        # Period Total
        pdf.setFillColor(self.color(self.secondary_text))
        pdf.drawRightString(right_x,y + 10,title_text)

    def color(self, value):
        return HexColor(value)