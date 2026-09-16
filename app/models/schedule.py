class Schedule:
    def __init__(self, template, start_date, end_date):
        self.template = template
        self.start_date = start_date
        self.end_date = end_date
        self.days = []

    def add_day(self, day):
        self.days.append(day)

    @property
    def total_hours(self):
        return sum(day.total_hours for day in self.days)

    @property
    def total_pay(self):
        return sum(day.total_pay for day in self.days)

    @property
    def weekly_totals(self):
        weeks = []

        for i in range(0, len(self.days), 7):
            week_days = self.days[i:i + 7]

            hours = sum(day.total_hours for day in week_days)
            pay = sum(day.total_pay for day in week_days)
            weeks.append({
                "start_date": week_days[0].date,
                "end_date": week_days[-1].date,
                "hours": hours,
                "pay": pay
            })

        return weeks

    def get_weekly_totals(self):
        weeks = []

        for i in range(0, len(self.days), 7):
            week_days = self.days[i:i + 7]

            weeks.append({
                "start_date": week_days[0].date,
                "end_date": week_days[-1].date,
                "hours": sum(day.total_hours for day in week_days),
                "pay": sum(day.total_pay for day in week_days)
            })

        return weeks