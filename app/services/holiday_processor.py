class HolidayProcessor:

    def apply_holidays(self, schedule, holidays):
        for holiday in holidays:
            self.apply_holiday(schedule, holiday)

    def apply_holiday(self, schedule, holiday):
        if holiday.start_time is None or holiday.end_time is None:
            self.apply_full_day_holiday(schedule, holiday)
        else:
            self.apply_partial_day_holiday(schedule, holiday)

    def apply_full_day_holiday(self, schedule, holiday):
        for day in schedule.days:

            if not (holiday.start_date <= day.date <= holiday.end_date):
                continue

            for shift in day.shifts:
                shift.holiday_hours = shift.hours
                shift.holiday_affected = True

    def apply_partial_day_holiday(self, schedule, holiday):
        holiday_duration = self.time_difference(
            holiday.start_time,
            holiday.end_time
        )

        for day in schedule.days:

            if day.date != holiday.start_date:
                continue

            allocated_holiday_hours = 0.0

            for shift in day.shifts:

                # Flexible shifts have no reliable time range,
                # so we cannot automatically allocate holiday hours.
                if shift.start_time is None or shift.end_time is None:
                    continue

                overlap = self.calculate_overlap(
                    shift.start_time,
                    shift.end_time,
                    holiday.start_time,
                    holiday.end_time
                )

                if overlap <= 0:
                    continue

                shift.holiday_hours = min(overlap, shift.hours)
                shift.holiday_affected = True

                allocated_holiday_hours += shift.holiday_hours

            day.unallocated_holiday_hours = max(
                0.0,
                holiday_duration - allocated_holiday_hours
            )

    def calculate_overlap(
        self,
        shift_start,
        shift_end,
        holiday_start,
        holiday_end
    ):
        shift_start_minutes = self.time_to_minutes(shift_start)
        shift_end_minutes = self.time_to_minutes(shift_end)
        holiday_start_minutes = self.time_to_minutes(holiday_start)
        holiday_end_minutes = self.time_to_minutes(holiday_end)

        overlap_start = max(
            shift_start_minutes,
            holiday_start_minutes
        )

        overlap_end = min(
            shift_end_minutes,
            holiday_end_minutes
        )

        if overlap_start >= overlap_end:
            return 0.0

        return (overlap_end - overlap_start) / 60

    def time_to_minutes(self, time_string):
        parts = time_string.split(":")
        hours = int(parts[0])
        minutes = int(parts[1])
        return hours * 60 + minutes

    def time_difference(self, start_time, end_time):
        start_minutes = self.time_to_minutes(start_time)
        end_minutes = self.time_to_minutes(end_time)

        return (end_minutes - start_minutes) / 60
        