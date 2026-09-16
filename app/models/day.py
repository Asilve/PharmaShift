class Day:
    def __init__(self, date):
        self.date = date
        self.day_of_week = date.dayOfWeek() - 1
        self.shifts = []

    def add_shift(self, shift):
        self.shifts.append(shift)

    @property
    def total_hours(self):
        return sum(shift.hours for shift in self.shifts)

    @property
    def total_pay(self):
        return sum(shift.hours * shift.rate for shift in self.shifts)