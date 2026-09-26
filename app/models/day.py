class Day:

    def __init__(self, date):
        self.date = date
        self.day_of_week = date.dayOfWeek() - 1
        self.shifts = []
        self.unallocated_holiday_hours = 0.0

    def add_shift(self, shift):
        self.shifts.append(shift)

    @property
    def total_hours(self):
        return sum(shift.hours for shift in self.shifts)

    @property
    def total_pay(self):
        return sum(shift.hours * shift.rate for shift in self.shifts)

    @property
    def worked_hours(self):
        return sum(shift.worked_hours for shift in self.shifts)

    @property
    def worked_pay(self):
        return sum(
            shift.worked_hours * shift.rate
            for shift in self.shifts
        )
    @property
    def has_unallocated_holiday(self):
        return self.unallocated_holiday_hours > 0