from PySide6.QtCore import QDate

from app.database.database import Database
from app.services.schedule_generator import ScheduleGenerator


def test_schedule_persistence():
    # --------------------------------------------------
    # 1. Create an isolated test database
    # --------------------------------------------------

    db = Database(":memory:")
    db.create_tables()

    # --------------------------------------------------
    # 2. Create a template
    # --------------------------------------------------

    template_id = db.add_template(
        name="Test Pharmacist",
        notes="Independent Prescriber",
        colour="#4A90E2"
    )

    db.add_shift(
        template_id=template_id,
        day_of_week=0,       # Monday
        start_time="09:00",
        end_time="17:00",
        hours=8.0,
        location="Test Surgery",
        rate=25.00
    )

    db.add_shift(
        template_id=template_id,
        day_of_week=2,       # Wednesday
        start_time=None,
        end_time=None,
        hours=0.75,
        location="Flexible Clinic",
        rate=30.00
    )

    # --------------------------------------------------
    # 3. Load the template
    # --------------------------------------------------

    template = db.get_template(template_id)

    assert template is not None
    assert template.name == "Test Pharmacist"
    assert template.notes == "Independent Prescriber"
    assert template.colour == "#4A90E2"
    assert len(template.shifts) == 2

    # --------------------------------------------------
    # 4. Generate a schedule
    # --------------------------------------------------

    generator = ScheduleGenerator()

    start_date = QDate(2026, 9, 14)
    end_date = QDate(2026, 9, 20)

    schedule = generator.generate(
        template,
        start_date,
        end_date
    )

    # --------------------------------------------------
    # 5. Check the generated schedule
    # --------------------------------------------------

    assert schedule.template.name == "Test Pharmacist"
    assert schedule.start_date == start_date
    assert schedule.end_date == end_date

    # One week = seven days
    assert len(schedule.days) == 7

    # Monday should have the 8-hour shift
    monday = schedule.days[0]

    assert monday.date == QDate(2026, 9, 14)
    assert len(monday.shifts) == 1
    assert monday.shifts[0].hours == 8.0
    assert monday.shifts[0].location == "Test Surgery"
    assert monday.shifts[0].rate == 25.00

    # Wednesday should have the 0.75-hour shift
    wednesday = schedule.days[2]

    assert len(wednesday.shifts) == 1
    assert wednesday.shifts[0].hours == 0.75
    assert wednesday.shifts[0].location == "Flexible Clinic"

    # --------------------------------------------------
    # 6. Save the schedule
    # --------------------------------------------------

    schedule_id = db.save_schedule(schedule)

    assert schedule_id is not None

    # --------------------------------------------------
    # 7. Load the saved schedule
    # --------------------------------------------------

    loaded_schedule = db.load_schedule(schedule_id)

    assert loaded_schedule is not None

    # --------------------------------------------------
    # 8. Verify the loaded schedule
    # --------------------------------------------------

    assert loaded_schedule.start_date == start_date
    assert loaded_schedule.end_date == end_date

    assert loaded_schedule.template.name == "Test Pharmacist"
    assert loaded_schedule.template.notes == "Independent Prescriber"
    assert loaded_schedule.template.colour == "#4A90E2"

    assert len(loaded_schedule.days) == 7

    # --------------------------------------------------
    # 9. Verify the saved shifts
    # --------------------------------------------------

    loaded_monday = loaded_schedule.days[0]

    assert len(loaded_monday.shifts) == 1

    loaded_shift = loaded_monday.shifts[0]

    assert loaded_shift.start_time == "09:00"
    assert loaded_shift.end_time == "17:00"
    assert loaded_shift.hours == 8.0
    assert loaded_shift.location == "Test Surgery"
    assert loaded_shift.rate == 25.00

    loaded_wednesday = loaded_schedule.days[2]

    assert len(loaded_wednesday.shifts) == 1
    assert loaded_wednesday.shifts[0].hours == 0.75
    assert loaded_wednesday.shifts[0].location == "Flexible Clinic"
    assert loaded_wednesday.shifts[0].rate == 30.00

    # --------------------------------------------------
    # 10. Verify calculated totals
    # --------------------------------------------------

    assert loaded_schedule.total_hours == 8.75

    assert loaded_schedule.total_pay == (
        (8.0 * 25.00) +
        (0.75 * 30.00)
    )

def test_saved_schedule_is_independent_of_template():
    # --------------------------------------------------
    # 1. Create database
    # --------------------------------------------------

    db = Database(":memory:")
    db.create_tables()

    # --------------------------------------------------
    # 2. Create template
    # --------------------------------------------------

    template_id = db.add_template(
        name="Original Name",
        notes="Original Notes",
        colour="#123456"
    )

    db.add_shift(
        template_id=template_id,
        day_of_week=0,
        start_time="09:00",
        end_time="17:00",
        hours=8.0,
        location="Original Surgery",
        rate=25.00
    )

    # --------------------------------------------------
    # 3. Generate schedule
    # --------------------------------------------------

    template = db.get_template(template_id)

    generator = ScheduleGenerator()

    schedule = generator.generate(
        template,
        QDate(2026, 9, 14),
        QDate(2026, 9, 20)
    )

    # --------------------------------------------------
    # 4. Save it
    # --------------------------------------------------

    schedule_id = db.save_schedule(schedule)

    # --------------------------------------------------
    # 5. Change the template
    # --------------------------------------------------

    db.update_template(
        template_id,
        name="Changed Name",
        notes="Changed Notes",
        colour="#FFFFFF"
    )

    db.update_shift(
        shift_id=template.shifts[0].id,
        day_of_week=0,
        start_time="10:00",
        end_time="18:00",
        hours=8.0,
        location="Changed Surgery",
        rate=50.00
    )

    # --------------------------------------------------
    # 6. Load the saved schedule
    # --------------------------------------------------

    loaded_schedule = db.load_schedule(schedule_id)

    # --------------------------------------------------
    # 7. Verify the ORIGINAL data survived
    # --------------------------------------------------

    assert loaded_schedule.template.name == "Original Name"
    assert loaded_schedule.template.notes == "Original Notes"
    assert loaded_schedule.template.colour == "#123456"

    monday = loaded_schedule.days[0]

    assert monday.shifts[0].start_time == "09:00"
    assert monday.shifts[0].end_time == "17:00"
    assert monday.shifts[0].location == "Original Surgery"
    assert monday.shifts[0].rate == 25.00

def test_saved_schedule_survives_template_deletion():
    db = Database(":memory:")
    db.create_tables()

    template_id = db.add_template(
        name="Temporary Pharmacist",
        notes="",
        colour="#ABCDEF"
    )

    db.add_shift(
        template_id=template_id,
        day_of_week=0,
        start_time="09:00",
        end_time="17:00",
        hours=8.0,
        location="Surgery",
        rate=25.00
    )

    template = db.get_template(template_id)

    generator = ScheduleGenerator()

    schedule = generator.generate(
        template,
        QDate(2026, 9, 14),
        QDate(2026, 9, 20)
    )

    schedule_id = db.save_schedule(schedule)

    # Delete the original recurring template
    db.delete_template(template_id)

    # Historical schedule should still exist
    loaded_schedule = db.load_schedule(schedule_id)

    assert loaded_schedule is not None
    assert loaded_schedule.template.name == "Temporary Pharmacist"
    assert loaded_schedule.days[0].shifts[0].hours == 8.0

def test_saving_schedule_twice_updates_existing_schedule():
    db = Database(":memory:")
    db.create_tables()

    template_id = db.add_template(
        name="Test Pharmacist",
        notes="",
        colour="#123456"
    )

    db.add_shift(
        template_id=template_id,
        day_of_week=0,
        start_time="09:00",
        end_time="17:00",
        hours=8.0,
        location="Surgery",
        rate=25.00
    )

    template = db.get_template(template_id)

    generator = ScheduleGenerator()

    schedule = generator.generate(
        template,
        QDate(2026, 9, 14),
        QDate(2026, 9, 20)
    )

    # First save
    first_id = db.save_schedule(schedule)

    assert schedule.id == first_id

    # Save again
    second_id = db.save_schedule(schedule)

    assert second_id == first_id
    assert schedule.id == first_id

    # There should still only be one saved schedule
    saved_schedules = db.get_saved_schedules()

    assert len(saved_schedules) == 1
    assert saved_schedules[0][0] == first_id

def test_saving_existing_schedule_updates_saved_data():
    db = Database(":memory:")
    db.create_tables()

    template_id = db.add_template(
        name="Test Pharmacist",
        notes="",
        colour="#123456"
    )

    db.add_shift(
        template_id=template_id,
        day_of_week=0,
        start_time="09:00",
        end_time="17:00",
        hours=8.0,
        location="Original Surgery",
        rate=25.00
    )

    template = db.get_template(template_id)

    generator = ScheduleGenerator()

    schedule = generator.generate(
        template,
        QDate(2026, 9, 14),
        QDate(2026, 9, 20)
    )

    # First save
    schedule_id = db.save_schedule(schedule)

    assert schedule_id == schedule.id

    # Change the schedule object directly
    monday = schedule.days[0]

    monday.shifts[0].location = "Changed Surgery"
    monday.shifts[0].rate = 30.00

    # Save again
    updated_id = db.save_schedule(schedule)

    assert updated_id == schedule_id

    # Load it again
    loaded_schedule = db.load_schedule(schedule_id)

    loaded_monday = loaded_schedule.days[0]
    loaded_shift = loaded_monday.shifts[0]

    assert loaded_shift.location == "Changed Surgery"
    assert loaded_shift.rate == 30.00

    # Still only one saved schedule
    saved_schedules = db.get_saved_schedules()

    assert len(saved_schedules) == 1