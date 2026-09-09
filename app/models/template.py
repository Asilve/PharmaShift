
class EmployeeTemplate:
    def __init__(self, name, colour, notes="", template_id=None):
        self.id = template_id
        self.name = name
        self.notes = notes
        self.colour = colour
        self.shifts = []