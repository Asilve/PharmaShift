class HolidayValidator:

    @staticmethod
    def validate(start_date,end_date,start_time=None,end_time=None,covered=False,covered_by=None):
        errors = []

        # Date validation
        if start_date is None:
            errors.append("Start date is required.")

        if end_date is None:
            errors.append("End date is required.")

        if start_date is not None and end_date is not None:

            if start_date > end_date:
                errors.append(
                    "End date cannot be before the start date."
                )

        # Time validation
        if (start_date is not None and end_date is not None):

            # Multi-day holiday
            if start_date != end_date:

                if start_time is not None:
                    errors.append("A holiday period cannot have a start time.")

                if end_time is not None:
                    errors.append("A holiday period cannot have an end time.")

            # Single-day holiday
            else:

                # One time without the other
                if (start_time is None and end_time is not None
                ):
                    errors.append("A partial-day holiday requires a start time.")

                if (
                    start_time is not None and end_time is None):
                    errors.append("A partial-day holiday requires an end time.")

                # Both times supplied
                if (start_time is not None and end_time is not None):
                    if start_time >= end_time:
                        errors.append("End time must be after the start time.")

        # Coverage validation
        if covered:
            if (covered_by is None or not str(covered_by).strip()):
                errors.append(
                    "A person must be specified when "
                    "the holiday is marked as covered."
                )

        else:
            if (covered_by is not None and str(covered_by).strip()):
                errors.append(
                    "A covered by person cannot be specified "
                    "unless the holiday is marked as covered."
                )
        return errors