import sqlite3

from models.shift import Shift
from models.template import EmployeeTemplate
from models.schedule import Schedule
from models.day import Day


class Database:
    def __init__(self, db_path="PharmaShift.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("PRAGMA foreign_keys = ON")

    def create_tables(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                colour TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT ''
            )
        """)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS shifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER NOT NULL,
                day_of_week INTEGER NOT NULL,
                start_time TEXT,
                end_time TEXT,
                hours REAL NOT NULL,
                location TEXT NOT NULL,
                rate REAL NOT NULL,

                FOREIGN KEY (template_id)
                    REFERENCES templates(id)
                    ON DELETE CASCADE
            )
        """)

        self.connection.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER,
                employee_name TEXT NOT NULL,
                employee_notes TEXT NOT NULL DEFAULT '',
                employee_colour TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS schedule_days (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                is_holiday INTEGER NOT NULL DEFAULT 0,

                FOREIGN KEY (schedule_id)
                    REFERENCES schedules(id)
                    ON DELETE CASCADE
            )
        """)

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS schedule_shifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_day_id INTEGER NOT NULL,
                start_time TEXT,
                end_time TEXT,
                hours REAL NOT NULL,
                holiday_hours REAL NOT NULL DEFAULT 0,
                rate REAL NOT NULL,
                location TEXT NOT NULL,
                holiday_affected INTEGER NOT NULL DEFAULT 0,
                covered INTEGER NOT NULL DEFAULT 0,
                covered_by TEXT,

                FOREIGN KEY (schedule_day_id)
                    REFERENCES schedule_days(id)
                    ON DELETE CASCADE
            )
        """)

        self.connection.commit()


    def add_template(self, name, notes, colour):
        cursor = self.connection.execute(
            """
            INSERT INTO templates (name, notes, colour)
            VALUES (?, ?, ?)
            """,
            (name, notes, colour)
        )

        self.connection.commit()

        return cursor.lastrowid

    def get_templates(self):
        cursor = self.connection.execute(
            """
            SELECT id, name, colour, notes
            FROM templates
            """
        )

        return cursor.fetchall()

    def update_template(self, template_id, name, notes, colour):
        self.connection.execute(
            """
            UPDATE templates
            SET name = ?, notes = ?, colour = ?
            WHERE id = ?
            """,
            (name, notes, colour, template_id)
        )

        self.connection.commit()

    def delete_template(self, template_id):
        self.connection.execute(
            """
            DELETE FROM templates
            WHERE id = ?
            """,
            (template_id,)
        )

        self.connection.commit()


    def add_shift(
        self,
        template_id,
        day_of_week,
        start_time,
        end_time,
        hours,
        location,
        rate
    ):
        self.connection.execute(
            """
            INSERT INTO shifts (
                template_id,
                day_of_week,
                start_time,
                end_time,
                hours,
                location,
                rate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                template_id,
                day_of_week,
                start_time,
                end_time,
                hours,
                location,
                rate
            )
        )

        self.connection.commit()

    def get_shifts(self, template_id):
        cursor = self.connection.execute(
            """
            SELECT
                id,
                day_of_week,
                start_time,
                end_time,
                hours,
                location,
                rate
            FROM shifts
            WHERE template_id = ?
            ORDER BY day_of_week, start_time
            """,
            (template_id,)
        )

        shifts = []

        for row in cursor.fetchall():
            shift = Shift(
                day_of_week=row[1],
                start_time=row[2],
                end_time=row[3],
                hours=row[4],
                location=row[5],
                rate=row[6],
                shift_id=row[0]
            )

            shifts.append(shift)

        return shifts

    def update_shift(
        self,
        shift_id,
        day_of_week,
        start_time,
        end_time,
        hours,
        location,
        rate
    ):
        self.connection.execute(
            """
            UPDATE shifts
            SET
                day_of_week = ?,
                start_time = ?,
                end_time = ?,
                hours = ?,
                location = ?,
                rate = ?
            WHERE id = ?
            """,
            (
                day_of_week,
                start_time,
                end_time,
                hours,
                location,
                rate,
                shift_id
            )
        )

        self.connection.commit()

    def delete_shift(self, shift_id):
        self.connection.execute(
            """
            DELETE FROM shifts
            WHERE id = ?
            """,
            (shift_id,)
        )

        self.connection.commit()

    def get_template(self, template_id):
        cursor = self.connection.execute(
            """
            SELECT id, name, colour, notes
            FROM templates
            WHERE id = ?
            """,
            (template_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        template = EmployeeTemplate(
            name=row[1],
            colour=row[2],
            notes=row[3],
            template_id=row[0]
        )

        template.shifts = self.get_shifts(template.id)

        return template

    def save_schedule(self, schedule):
        template = schedule.template

        now = self.connection.execute(
            "SELECT CURRENT_TIMESTAMP"
        ).fetchone()[0]

        if schedule.id is None:
            cursor = self.connection.execute(
                """
                INSERT INTO schedules (
                    template_id,
                    employee_name,
                    employee_notes,
                    employee_colour,
                    start_date,
                    end_date,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    template.id,
                    template.name,
                    template.notes,
                    template.colour,
                    schedule.start_date.toString("yyyy-MM-dd"),
                    schedule.end_date.toString("yyyy-MM-dd"),
                    now,
                    now
                )
            )

            schedule.id = cursor.lastrowid

        else:
            self.connection.execute(
                """
                UPDATE schedules
                SET
                    template_id = ?,
                    employee_name = ?,
                    employee_notes = ?,
                    employee_colour = ?,
                    start_date = ?,
                    end_date = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    template.id,
                    template.name,
                    template.notes,
                    template.colour,
                    schedule.start_date.toString("yyyy-MM-dd"),
                    schedule.end_date.toString("yyyy-MM-dd"),
                    now,
                    schedule.id
                )
            )

            self.connection.execute(
                """
                DELETE FROM schedule_days
                WHERE schedule_id = ?
                """,
                (schedule.id,)
            )

        for day in schedule.days:
            day_cursor = self.connection.execute(
                """
                INSERT INTO schedule_days (
                    schedule_id,
                    date,
                    is_holiday
                )
                VALUES (?, ?, ?)
                """,
                (
                    schedule.id,
                    day.date.toString("yyyy-MM-dd"),
                    int(getattr(day, "is_holiday", False))
                )
            )

            schedule_day_id = day_cursor.lastrowid

            for shift in day.shifts:
                self.connection.execute(
                    """
                    INSERT INTO schedule_shifts (
                        schedule_day_id,
                        start_time,
                        end_time,
                        hours,
                        holiday_hours,
                        rate,
                        location,
                        holiday_affected,
                        covered,
                        covered_by
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        schedule_day_id,
                        shift.start_time,
                        shift.end_time,
                        shift.hours,
                        getattr(shift, "holiday_hours", 0),
                        shift.rate,
                        shift.location,
                        int(getattr(shift, "holiday_affected", False)),
                        int(getattr(shift, "covered", False)),
                        getattr(shift, "covered_by", None)
                    )
                )

        self.connection.commit()

        return schedule.id

    def get_saved_schedules(self):
        cursor = self.connection.execute(
            """
            SELECT
                id,
                employee_name,
                employee_notes,
                employee_colour,
                start_date,
                end_date,
                created_at,
                updated_at
            FROM schedules
            ORDER BY updated_at DESC, id DESC
            """
        )

        return cursor.fetchall()

    def load_schedule(self, schedule_id):
        cursor = self.connection.execute(
            """
            SELECT
                id,
                template_id,
                employee_name,
                employee_notes,
                employee_colour,
                start_date,
                end_date
            FROM schedules
            WHERE id = ?
            """,
            (schedule_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        schedule_db_id = row[0]
        template_id = row[1]

        employee_name = row[2]
        employee_notes = row[3]
        employee_colour = row[4]

        start_date = self._date_from_string(row[5])
        end_date = self._date_from_string(row[6])

        template = EmployeeTemplate(
            name=employee_name,
            colour=employee_colour,
            notes=employee_notes,
            template_id=template_id
        )

        schedule = Schedule(
            template=template,
            start_date=start_date,
            end_date=end_date,
            schedule_id=schedule_db_id
        )

        days_cursor = self.connection.execute(
            """
            SELECT
                id,
                date,
                is_holiday
            FROM schedule_days
            WHERE schedule_id = ?
            ORDER BY date
            """,
            (schedule_db_id,)
        )

        for day_row in days_cursor.fetchall():
            schedule_day_id = day_row[0]

            day = Day(
                self._date_from_string(day_row[1])
            )

            day.is_holiday = bool(day_row[2])

            shifts_cursor = self.connection.execute(
                """
                SELECT
                    id,
                    start_time,
                    end_time,
                    hours,
                    holiday_hours,
                    rate,
                    location,
                    holiday_affected,
                    covered,
                    covered_by
                FROM schedule_shifts
                WHERE schedule_day_id = ?
                ORDER BY start_time
                """,
                (schedule_day_id,)
            )

            for shift_row in shifts_cursor.fetchall():
                shift = Shift(
                    day_of_week=day.day_of_week,
                    start_time=shift_row[1],
                    end_time=shift_row[2],
                    hours=shift_row[3],
                    location=shift_row[6],
                    rate=shift_row[5],
                    shift_id=shift_row[0]
                )

                shift.holiday_hours = shift_row[4]
                shift.holiday_affected = bool(shift_row[7])
                shift.covered = bool(shift_row[8])
                shift.covered_by = shift_row[9]

                day.add_shift(shift)

            schedule.add_day(day)

        return schedule

    def delete_schedule(self, schedule_id):
        cursor = self.connection.cursor()

        cursor.execute(
            "DELETE FROM schedules WHERE id = ?",
            (schedule_id,)
        )

        self.connection.commit()

    def _date_from_string(self, date_string):
        from PySide6.QtCore import QDate

        return QDate.fromString(
            date_string,
            "yyyy-MM-dd"
        )