from datetime import datetime, timedelta

class NotificationScheduler:
    """
    Generates notification follow-ups based on risk level.
    """

    def generate_schedule(self, risk_level):
        today = datetime.now()

        if risk_level == "Urgent":
            return [
                {"date": today.strftime("%Y-%m-%d"), "type": "Immediate clinical visit"},
                {"date": (today + timedelta(days=3)).strftime("%Y-%m-%d"), "type": "Follow-up test reminder"},
                {"date": (today + timedelta(days=7)).strftime("%Y-%m-%d"), "type": "Lifestyle adherence check"},
            ]

        elif risk_level == "High":
            return [
                {"date": today.strftime("%Y-%m-%d"), "type": "Doctor appointment reminder"},
                {"date": (today + timedelta(days=14)).strftime("%Y-%m-%d"), "type": "Follow-up reminder"},
                {"date": (today + timedelta(days=30)).strftime("%Y-%m-%d"), "type": "Check progress"},
            ]

        elif risk_level == "Medium":
            return [
                {"date": today.strftime("%Y-%m-%d"), "type": "Health tips reminder"},
                {"date": (today + timedelta(days=30)).strftime("%Y-%m-%d"), "type": "Monthly progress check"},
            ]

        else:  # Low risk
            return [
                {"date": (today + timedelta(days=30)).strftime("%Y-%m-%d"), "type": "Check progress"},
                {"date": (today + timedelta(days=90)).strftime("%Y-%m-%d"), "type": "Routine health check reminder"},
            ]

    # For backward compatibility with your current app.py
    def create_schedule(self, patient_id=None, risk_level="medium", gender="unknown", age=40):
        """
        Create notification schedule based on patient profile
        """
        schedule = []

        if risk_level == "urgent":
            schedule.append({"time": "08:00", "message": "Urgent health check reminder"})
            schedule.append({"time": "20:00", "message": "Log symptoms daily"})
        elif risk_level == "high":
            schedule.append({"time": "09:00", "message": "Track daily exercise"})
            schedule.append({"time": "19:00", "message": "Healthy dinner reminder"})
        else:
            schedule.append({"time": "10:00", "message": "Hydration check"})
            schedule.append({"time": "18:00", "message": "Go for a walk"})

        return {
            "patient_id": patient_id,
            "risk_level": risk_level,
            "schedule": schedule
        }

