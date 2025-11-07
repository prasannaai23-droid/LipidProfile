import sqlite3
import threading

class DatabaseHandler:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path
        self.lock = threading.Lock()  # Prevent database locking issues
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _create_table(self):
        with self.lock:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT,
                    risk_level TEXT
                )
            """)
            conn.commit()
            conn.close()

    def save_result(self, patient_id, risk_level):
        with self.lock:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO patients (patient_id, risk_level) VALUES (?, ?)",
                (patient_id, risk_level)
            )
            conn.commit()
            conn.close()

    def get_all_results(self):
        with self.lock:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM patients")
            rows = cursor.fetchall()
            conn.close()
            return rows
