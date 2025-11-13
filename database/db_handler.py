import sqlite3
import json
from datetime import datetime
import os
import threading

class DatabaseHandler:
    def __init__(self, db_path="patient_data.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.lock = threading.Lock()  # Prevent database locking issues
        self.create_tables()
    
    def _connect(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def create_tables(self):
        """Create necessary database tables"""
        with self.lock:
            conn = self._connect()
            cursor = conn.cursor()
            
            # Assessments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    risk_level TEXT,
                    management_type TEXT,
                    lifestyle_plan TEXT,
                    notification_schedule TEXT,
                    lipid_values TEXT,
                    extracted_data TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
                )
            ''')
            
            # Patients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    patient_id TEXT PRIMARY KEY,
                    patient_name TEXT,
                    age INTEGER,
                    sex TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Database tables created/verified")
    
    def save_assessment(self, assessment_data):
        """Save assessment to database"""
        try:
            with self.lock:
                conn = self._connect()
                cursor = conn.cursor()
                
                # Insert or update patient info
                patient_id = assessment_data.get('patient_id')
                extracted = assessment_data.get('extracted_data', {})
                
                cursor.execute('''
                    INSERT OR REPLACE INTO patients (patient_id, patient_name, age, sex)
                    VALUES (?, ?, ?, ?)
                ''', (
                    patient_id,
                    extracted.get('patient_name'),
                    extracted.get('age'),
                    extracted.get('sex')
                ))
                
                # Insert assessment
                cursor.execute('''
                    INSERT INTO assessments (
                        patient_id, timestamp, risk_level, management_type,
                        lifestyle_plan, notification_schedule, lipid_values, extracted_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    patient_id,
                    assessment_data.get('timestamp', datetime.now()),
                    assessment_data.get('risk_analysis', {}).get('risk_level'),
                    assessment_data.get('management_type'),
                    json.dumps(assessment_data.get('lifestyle_plan')),
                    json.dumps(assessment_data.get('notification_schedule')),
                    json.dumps(assessment_data.get('lipid_values')),
                    json.dumps(extracted)
                ))
                
                conn.commit()
                conn.close()
                print(f"✅ Assessment saved for patient {patient_id}")
                return True
                
        except Exception as e:
            print(f"❌ Database save error: {e}")
            return False
    
    def get_patient_history(self, patient_id):
        """Get all assessments for a patient"""
        try:
            with self.lock:
                conn = self._connect()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT timestamp, risk_level, management_type, lipid_values
                    FROM assessments
                    WHERE patient_id = ?
                    ORDER BY timestamp DESC
                ''', (patient_id,))
                
                rows = cursor.fetchall()
                conn.close()
                
                history = []
                for row in rows:
                    history.append({
                        'timestamp': row[0],
                        'risk_level': row[1],
                        'management_type': row[2],
                        'lipid_values': json.loads(row[3]) if row[3] else {}
                    })
                
                return history
                
        except Exception as e:
            print(f"❌ Database read error: {e}")
            return []
