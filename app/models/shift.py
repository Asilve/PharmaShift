class Shift:
    def __init__(self, day_of_week, start_time=None, end_time=None, hours=None, location="", rate=0.0, shift_id=None):
        self.id = shift_id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time
        self.hours = hours
        self.location = location
        self.rate = rate