# ...existing code...
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import datetime
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Import custom modules
from ml_model.risk_classifier import RiskClassifier
from ml_model.lifestyle_generator import LifestyleGenerator
from database.db_handler import DatabaseHandler
from ml_model.notification_scheduler import NotificationScheduler


# Get the absolute path to the templates folder
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')

# Initialize Flask app with correct template and static folders
app = Flask(__name__,
            template_folder=template_dir,
            static_folder=static_dir)
CORS(app)

# Initialize components
print("Initializing application components...")
try:
    db = DatabaseHandler()
    print("✓ Database initialized")
except Exception as e:
    print(f"⚠ Database initialization warning: {e}")
    db = None

try:
    risk_model = RiskClassifier()
    print("✓ Risk classifier initialized")
except Exception as e:
    print(f"✗ Risk classifier error: {e}")
    risk_model = None

try:
    lifestyle_gen = LifestyleGenerator()
    print("✓ Lifestyle generator initialized")
except Exception as e:
    print(f"✗ Lifestyle generator error: {e}")
    lifestyle_gen = None

try:
    scheduler = NotificationScheduler()
    print("✓ Notification scheduler initialized")
except Exception as e:
    print(f"✗ Scheduler error: {e}")
    scheduler = None

@app.route('/')
def home():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/analyze-lipid-profile', methods=['POST'])
def analyze_lipid_profile():
    """
    Analyze lipid profile and classify risk
    Expected input: {
        'patient_id': str,
        'total_cholesterol': float,
        'ldl': float,
        'hdl': float,
        'triglycerides': float,
        'blood_glucose': float,
        'age': int,
        'gender': str,
        'bmi': float,
        'smoking': bool,
        'family_history': bool,
        'existing_conditions': list
    }
    """
    try:
        data = request.json

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['patient_id', 'ldl', 'hdl', 'triglycerides', 'blood_glucose', 'age', 'gender']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Step 1: Risk Classification
        from ml_model.predict import predict_risk

        result = predict_risk(data)
        risk_analysis = {
            "risk_level": result.get("risk_label"),
            "confidence": result.get("confidence")
        }

        # Step 2: Medical Management vs Lifestyle Classification
        management_type = None
        if risk_model:
            management_type = risk_model.classify_management(risk_analysis)
        else:
            management_type = 'unknown'

        # Step 3: Generate Personalized Plan
        lifestyle_plan = None
        if lifestyle_gen:
            lifestyle_plan = lifestyle_gen.generate_plan(
                risk_level=risk_analysis['risk_level'],
                patient_data=data,
                management_type=management_type
            )
        else:
            lifestyle_plan = {'note': 'Lifestyle generator not available'}

        # Step 4: Schedule Notifications
        notification_schedule = None
        if scheduler:
            notification_schedule = scheduler.create_schedule(
                patient_id=data['patient_id'],
                risk_level=risk_analysis['risk_level'],
            )
        else:
            notification_schedule = {'note': 'Scheduler not available'}

        # Step 5: Save to Database (if available)
        if db:
            try:
                assessment_id = db.save_assessment({
                    'patient_id': data['patient_id'],
                    'timestamp': datetime.datetime.now(),
                    'risk_analysis': risk_analysis,
                    'management_type': management_type,
                    'lifestyle_plan': lifestyle_plan,
                    'notification_schedule': notification_schedule
                })
                print(f"✓ Assessment saved with ID: {assessment_id}")
            except Exception as e:
                print(f"⚠ Warning: Could not save to database: {e}")

        return jsonify({
            'success': True,
            'risk_analysis': risk_analysis,
            'management_type': management_type,
            'lifestyle_plan': lifestyle_plan,
            'notification_schedule': notification_schedule,
            'safety_disclaimer': get_safety_disclaimer()
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in analyze_lipid_profile: {error_details}")
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_details if app.debug else None
        }), 500

@app.route('/api/track-adherence', methods=['POST'])
def track_adherence():
    """Track patient adherence to lifestyle plan"""
    try:
        data = request.json

        if not data or 'patient_id' not in data or 'status' not in data:
            return jsonify({'success': False, 'error': 'Invalid data'}), 400

        if db:
            db.log_adherence(
                patient_id=data['patient_id'],
                activity=data.get('activity', 'Unknown'),
                status=data['status'],  # 'done' or 'skip'
                timestamp=datetime.datetime.now()
            )

            # Check for escalation
            adherence_rate = db.get_adherence_rate(data['patient_id'], days=7)

            escalation = None
            if adherence_rate < 0.5:  # Less than 50%
                escalation = {
                    'flag': 'low_adherence',
                    'message': 'Patient showing poor adherence (<50%). Clinical follow-up recommended.',
                    'urgency': 'medium',
                    'adherence_rate': round(adherence_rate * 100, 1)
                }
            elif adherence_rate < 0.7:  # Less than 70%
                escalation = {
                    'flag': 'moderate_adherence',
                    'message': 'Patient adherence needs improvement. Consider motivational interview.',
                    'urgency': 'low',
                    'adherence_rate': round(adherence_rate * 100, 1)
                }

            return jsonify({
                'success': True,
                'adherence_rate': round(adherence_rate * 100, 1),
                'escalation': escalation
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Adherence logged (database not available)'
            })

    except Exception as e:
        import traceback
        print(f"Error in track_adherence: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/patient-history/<patient_id>', methods=['GET'])
def get_patient_history(patient_id):
    """Get patient's assessment history"""
    try:
        if db:
            history = db.get_patient_history(patient_id)
            return jsonify({'success': True, 'history': history})
        else:
            return jsonify({'success': False, 'error': 'Database not available'}), 503
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notifications/<patient_id>', methods=['GET'])
def get_notifications(patient_id):
    """Get pending notifications for patient"""
    try:
        if scheduler:
            notifications = scheduler.get_pending_notifications(patient_id)
            return jsonify({'success': True, 'notifications': notifications})
        else:
            return jsonify({'success': False, 'error': 'Scheduler not available'}), 503
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'components': {
            'database': db is not None,
            'risk_classifier': risk_model is not None,
            'lifestyle_generator': lifestyle_gen is not None,
            'scheduler': scheduler is not None
        }
    })

def get_safety_disclaimer():
    """Medical safety disclaimer"""
    return """
    ⚠️ IMPORTANT MEDICAL DISCLAIMER:

    This system provides educational information and risk assessment support only.
    It does NOT replace professional medical diagnosis or treatment.

    • Always consult your healthcare provider before making medical decisions
    • Urgent cases require immediate medical attention
    • Lipid management requires ongoing medical supervision
    • Individual results may vary based on unique health conditions
    • This tool is designed to assist, not replace, clinical judgment

    In case of chest pain, difficulty breathing, or other emergency symptoms,
    call emergency services immediately.
    """

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 Lipid Profile Risk Assessment System")
    print("=" * 60)
    print(f"Template folder: {template_dir}")
    print(f"Static folder: {static_dir}")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("Press CTRL+C to stop")
    print("=" * 60)

    app.run(debug=True, port=5000, host='0.0.0.0')