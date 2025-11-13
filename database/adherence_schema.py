import sqlite3
from datetime import datetime, timedelta
import json

class AdherenceTracker:
    def __init__(self, db_path='database/cardio_health.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize adherence tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Daily Activity Log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                activity_date DATE NOT NULL,
                diet_followed BOOLEAN DEFAULT 0,
                exercise_completed BOOLEAN DEFAULT 0,
                medication_taken BOOLEAN DEFAULT 0,
                water_intake_met BOOLEAN DEFAULT 0,
                sleep_quality INTEGER DEFAULT 0,
                stress_level INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(patient_id, activity_date)
            )
        ''')
        
        # Medication Adherence
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medication_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                medication_name TEXT NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                taken_time TIMESTAMP,
                status TEXT DEFAULT 'pending',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Diet Log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diet_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                log_date DATE NOT NULL,
                meal_type TEXT NOT NULL,
                foods_consumed TEXT,
                calories INTEGER,
                saturated_fat REAL,
                cholesterol REAL,
                fiber REAL,
                compliance_score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Exercise Log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercise_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                exercise_date DATE NOT NULL,
                exercise_type TEXT NOT NULL,
                duration_minutes INTEGER,
                intensity TEXT,
                calories_burned INTEGER,
                heart_rate_avg INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Lipid Test Results (for tracking progress)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lipid_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                test_date DATE NOT NULL,
                total_cholesterol REAL,
                ldl REAL,
                hdl REAL,
                triglycerides REAL,
                vldl REAL,
                risk_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Adherence Scores (calculated metrics)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS adherence_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                week_start DATE NOT NULL,
                week_end DATE NOT NULL,
                diet_score REAL,
                exercise_score REAL,
                medication_score REAL,
                overall_score REAL,
                streak_days INTEGER,
                total_active_days INTEGER,
                achievements TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Patient Goals
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patient_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                goal_type TEXT NOT NULL,
                target_value REAL,
                current_value REAL,
                start_date DATE,
                target_date DATE,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Notifications & Reminders
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT,
                scheduled_time TIMESTAMP,
                sent_time TIMESTAMP,
                status TEXT DEFAULT 'pending',
                read_status BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Adherence tracking database initialized")
    
    def log_daily_activity(self, patient_id, date, activities):
        """Log daily activities for a patient"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO daily_activities 
                (patient_id, activity_date, diet_followed, exercise_completed, 
                medication_taken, water_intake_met, sleep_quality, stress_level, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_id,
                date,
                activities.get('diet_followed', 0),
                activities.get('exercise_completed', 0),
                activities.get('medication_taken', 0),
                activities.get('water_intake_met', 0),
                activities.get('sleep_quality', 0),
                activities.get('stress_level', 0),
                activities.get('notes', '')
            ))
            
            conn.commit()
            return {"success": True, "message": "Daily activity logged"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def calculate_adherence_score(self, patient_id, start_date, end_date):
        """Calculate adherence score for a date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get daily activities
        cursor.execute('''
            SELECT 
                COUNT(*) as total_days,
                SUM(diet_followed) as diet_days,
                SUM(exercise_completed) as exercise_days,
                SUM(medication_taken) as medication_days,
                SUM(water_intake_met) as water_days,
                AVG(sleep_quality) as avg_sleep,
                AVG(stress_level) as avg_stress
            FROM daily_activities
            WHERE patient_id = ? AND activity_date BETWEEN ? AND ?
        ''', (patient_id, start_date, end_date))
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            total_days = result[0]
            
            # Calculate individual scores (0-100)
            diet_score = (result[1] / total_days) * 100 if result[1] else 0
            exercise_score = (result[2] / total_days) * 100 if result[2] else 0
            medication_score = (result[3] / total_days) * 100 if result[3] else 0
            water_score = (result[4] / total_days) * 100 if result[4] else 0
            sleep_score = (result[5] / 10) * 100 if result[5] else 0  # Assuming 0-10 scale
            stress_score = 100 - ((result[6] / 10) * 100) if result[6] else 50  # Lower stress is better
            
            # Overall adherence score (weighted average)
            overall_score = (
                diet_score * 0.30 +
                exercise_score * 0.25 +
                medication_score * 0.25 +
                water_score * 0.10 +
                sleep_score * 0.05 +
                stress_score * 0.05
            )
            
            return {
                "total_days": total_days,
                "diet_score": round(diet_score, 2),
                "exercise_score": round(exercise_score, 2),
                "medication_score": round(medication_score, 2),
                "water_score": round(water_score, 2),
                "sleep_score": round(sleep_score, 2),
                "stress_score": round(stress_score, 2),
                "overall_score": round(overall_score, 2)
            }
        
        return None
    
    def get_current_streak(self, patient_id):
        """Calculate current consecutive days streak"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT activity_date, 
                   (diet_followed + exercise_completed + medication_taken + water_intake_met) as daily_total
            FROM daily_activities
            WHERE patient_id = ?
            ORDER BY activity_date DESC
        ''', (patient_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return 0
        
        streak = 0
        prev_date = None
        
        for date_str, daily_total in results:
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Check if at least 3 out of 4 activities completed
            if daily_total >= 3:
                if prev_date is None:
                    streak = 1
                elif (prev_date - current_date).days == 1:
                    streak += 1
                else:
                    break
                prev_date = current_date
            else:
                break
        
        return streak
    
    def predict_adherence_risk(self, patient_id, days=30):
        """Predict likelihood of patient dropping off"""
        score_data = self.calculate_adherence_score(
            patient_id,
            (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d')
        )
        
        if not score_data:
            return {"risk": "unknown", "confidence": 0}
        
        overall_score = score_data['overall_score']
        
        # Risk classification
        if overall_score >= 80:
            risk = "low"
            confidence = 95
        elif overall_score >= 60:
            risk = "medium"
            confidence = 75
        elif overall_score >= 40:
            risk = "high"
            confidence = 85
        else:
            risk = "very_high"
            confidence = 90
        
        return {
            "risk": risk,
            "confidence": confidence,
            "overall_score": overall_score,
            "recommendation": self._get_intervention_message(risk, score_data)
        }
    
    def _get_intervention_message(self, risk, score_data):
        """Generate intervention recommendations"""
        if risk == "very_high":
            return "URGENT: Patient shows very low adherence. Immediate intervention needed."
        elif risk == "high":
            weak_areas = []
            if score_data['diet_score'] < 50:
                weak_areas.append("diet")
            if score_data['exercise_score'] < 50:
                weak_areas.append("exercise")
            if score_data['medication_score'] < 50:
                weak_areas.append("medication")
            
            return f"Patient struggling with: {', '.join(weak_areas)}. Consider counseling or adjusted plan."
        elif risk == "medium":
            return "Patient showing moderate adherence. Continue monitoring and provide encouragement."
        else:
            return "Patient maintaining excellent adherence. Continue current plan."