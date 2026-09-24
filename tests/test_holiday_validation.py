from PySide6.QtCore import QDate

from app.services.holiday_validator import HolidayValidator


def test_holiday_validation():

    # Valid full-day holiday
    errors = HolidayValidator.validate(
        start_date=QDate(2026, 12, 24),
        end_date=QDate(2026, 12, 24)
    )

    print("Full day:", errors)


    # Valid period
    errors = HolidayValidator.validate(
        start_date=QDate(2026, 12, 24),
        end_date=QDate(2026, 12, 28)
    )

    print("Period:", errors)


    # Valid partial day
    errors = HolidayValidator.validate(
        start_date=QDate(2026, 12, 24),
        end_date=QDate(2026, 12, 24),
        start_time="12:00",
        end_time="16:00"
    )

    print("Partial day:", errors)


    # Invalid date order
    errors = HolidayValidator.validate(
        start_date=QDate(2026, 12, 28),
        end_date=QDate(2026, 12, 24)
    )

    print("Bad dates:", errors)


    # Invalid period with times
    errors = HolidayValidator.validate(
        start_date=QDate(2026, 12, 24),
        end_date=QDate(2026, 12, 28),
        start_time="12:00",
        end_time="16:00"
    )

    print("Period with times:", errors)


    # Invalid partial day
    errors = HolidayValidator.validate(
        start_date=QDate(2026, 12, 24),
        end_date=QDate(2026, 12, 24),
        start_time="16:00",
        end_time="12:00"
    )

    print("Bad times:", errors)


    # Invalid coverage
    errors = HolidayValidator.validate(
        start_date=QDate(2026, 12, 24),
        end_date=QDate(2026, 12, 24),
        covered=True,
        covered_by=None
    )

    print("Bad coverage:", errors)


    # Valid coverage
    errors = HolidayValidator.validate(
        start_date=QDate(2026, 12, 24),
        end_date=QDate(2026, 12, 24),
        covered=True,
        covered_by="External locum"
    )

    print("Valid coverage:", errors)

if __name__ == "__main__":
    test_holiday_validation()