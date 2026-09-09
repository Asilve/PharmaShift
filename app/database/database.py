import sqlite3


class Database:
    def __init__(self, db_path="PharmaShift.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)

    def create_tables(self):
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                colour TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT ''
            )
        """)

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