import sqlite3
from models.shift import Shift
from models.template import EmployeeTemplate

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

        self.connection.execute(
            """
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
            """
        )

        self.connection.commit()

    
    def add_template(self, name, notes, colour):
        self.connection.execute(
            """
            INSERT INTO templates (name, notes, colour)
            VALUES (?, ?, ?)
            """,
            (name, notes, colour)
        )
        self.connection.commit()

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

    def add_shift(self, template_id, day_of_week, start_time, end_time, hours, location, rate):
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
            (template_id, day_of_week, start_time, end_time, hours, location, rate)
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
            shift = Shift(day_of_week=row[1], start_time=row[2], end_time=row[3], hours=row[4], location=row[5], rate=row[6], shift_id=row[0])
            shifts.append(shift)

        return shifts


    def update_shift(self, shift_id, day_of_week, start_time, end_time, hours, location, rate):
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
            (day_of_week, start_time, end_time, hours, location, rate, shift_id)
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

        template = EmployeeTemplate(name=row[1], colour=row[2], notes=row[3], template_id=row[0])

        template.shifts = self.get_shifts(template.id)

        return template
    