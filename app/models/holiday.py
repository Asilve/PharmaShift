class Holiday:

    def __init__(self,template_id,start_date,end_date,start_time=None,end_time=None,covered=False,covered_by=None,holiday_id=None):
        self.id = holiday_id
        self.template_id = template_id
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.covered = covered
        self.covered_by = covered_by