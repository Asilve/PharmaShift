from models.schedule import Schedule
from models.day import Day
from models.shift import Shift


class ScheduleGenerator:

    def generate(self, template, start_date, end_date):
        schedule = Schedule(template=template, start_date=start_date, end_date=end_date)

        first_monday = start_date.addDays(-(start_date.dayOfWeek() - 1))
        last_sunday = end_date.addDays(7 - end_date.dayOfWeek())
        current_date = first_monday

        while current_date <= last_sunday:
            day = Day(current_date)
            schedule.add_day(day)
            current_date = current_date.addDays(1)
        self.populate_shifts(schedule)

        return schedule

    def populate_shifts(self, schedule):
        for day in schedule.days:

            if day.date < schedule.start_date or day.date > schedule.end_date:
                continue

            for template_shift in schedule.template.shifts:
                if template_shift.day_of_week == day.day_of_week:
                    shift = self.copy_shift(template_shift)
                    day.add_shift(shift)

    def copy_shift(self, template_shift):
        return Shift(
            day_of_week=template_shift.day_of_week,
            start_time=template_shift.start_time,
            end_time=template_shift.end_time,
            hours=template_shift.hours,
            location=template_shift.location,
            rate=template_shift.rate
        )