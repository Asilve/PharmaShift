class Shift:
    def __init__(self,day_of_week,start_time=None,end_time=None,hours=None,location="",rate=0.0,shift_id=None,holiday_hours=0.0,holiday_affected=False,covered=False,covered_by=""):
        self.id = shift_id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.hours = hours
        self.location = location
        self.rate = rate

        # Holiday information
        self.holiday_hours = holiday_hours
        self.holiday_affected = holiday_affected

        # Coverage information
        self.covered = covered
        self.covered_by = covered_by

    @property
    def worked_hours(self):
        return max(0.0, self.hours - self.holiday_hours)