import os
os.environ['GLOG_minloglevel'] = '2'  # Suppress PaddleOCR logs

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import datetime
import sys
import traceback
import numpy as np
import pickle
import sqlite3

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Import custom modules
from ml_model.risk_classifier import RiskClassifier
from ml_model.lifestyle_generator import LifestyleGenerator
from database.db_handler import DatabaseHandler
from ml_model.notification_scheduler import NotificationScheduler
from ml_model.extract_text_from_image import extract_lipid_values
from database.adherence_schema import AdherenceTracker



# Get paths
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Create uploads folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print("Initializing components...")
db = DatabaseHandler()
risk_model = RiskClassifier()
lifestyle_gen = LifestyleGenerator()
scheduler = NotificationScheduler()
adherence_tracker = AdherenceTracker()

# Load ML model
MODEL_PATH = 'models/lipid_model.pkl'
model = None

try:
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        print("✅ Model loaded successfully")
    else:
        print("⚠️ Model file not found. Using rule-based prediction.")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("⚠️ Using rule-based prediction.")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------------
# FRONTEND ROUTES
# ------------------------
@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/upload")
def upload_page():
    return render_template("upload.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/report")
def report_page():
    return render_template("report.html")

@app.route("/about")
def about_page():
    return render_template("about.html")

# ------------------------
# API ROUTES
# ------------------------
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Lipid Profile Risk Assessment System',
        'version': '1.0.0',
        'components': {
            'database': db is not None,
            'risk_model': risk_model is not None,
            'lifestyle_generator': lifestyle_gen is not None,
            'scheduler': scheduler is not None
        }
    })

@app.route("/api/upload-report", methods=["POST"])
def upload_report():
    """Upload medical report image and extract lipid values using OCR"""
    try:
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({
                "success": False, 
                "error": "Invalid file type. Only PNG, JPG, JPEG allowed"
            }), 400

        # Get patient ID from form data
        patient_id = request.form.get("patient_id", "unknown")

        # Save uploaded file securely
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        print(f"\n🔍 Processing uploaded file: {save_path}")

        # Extract lipid values using OCR
        vals = extract_lipid_values(save_path)
        
        print("✅ OCR Extraction Result:")
        print(vals)

        # Check for extraction errors
        if not vals or "error" in vals:
            error_msg = vals.get("error", "OCR extraction failed")
            return jsonify({
                "success": False, 
                "error": error_msg, 
                "raw_text": vals.get("raw_text", ""),
                "extracted": vals.get("extracted", {})
            }), 400

        # Normalize keys to match backend expectations
        payload = {
            "patient_id": patient_id,
            "total_cholesterol": vals.get("total_cholesterol"),
            "ldl": vals.get("ldl"),
            "hdl": vals.get("hdl"),
            "triglycerides": vals.get("triglycerides"),
            "vldl": vals.get("vldl"),
            "non_hdl": vals.get("non_hdl"),
            "tc_hdl_ratio": vals.get("tc_hdl_ratio"),
            "tg_hdl_ratio": vals.get("tg_hdl_ratio"),
            "ldl_hdl_ratio": vals.get("ldl_hdl_ratio"),
            "patient_name": vals.get("patient_name"),
            "age": vals.get("age"),
            "sex": vals.get("sex"),
            "report_date": vals.get("report_date")
        }

        # Validate required fields
        required_fields = ["total_cholesterol", "ldl", "hdl", "triglycerides"]
        missing = [f for f in required_fields if not payload.get(f)]
        
        if missing:
            return jsonify({
                "success": False,
                "error": f"Missing required lipid values: {', '.join(missing)}",
                "extracted": payload
            }), 400

        return jsonify({
            "success": True, 
            "data": payload,
            "message": "Successfully extracted lipid profile values"
        }), 200

    except Exception as e:
        print(f"\n❌ Upload Error: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "error": f"Server error: {str(e)}"
        }), 500


@app.route('/api/analyze-lipid-profile', methods=['POST'])
def analyze_lipid_profile():
    """Analyze lipid profile and generate risk assessment with lifestyle recommendations"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['patient_id', 'total_cholesterol', 'ldl', 'hdl', 'triglycerides']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Predict risk level
        from ml_model.predict import predict_risk
        result_label = predict_risk(
            float(data['total_cholesterol']),
            float(data['ldl']),
            float(data['hdl']),
            float(data['triglycerides'])
        )

        # Generate comprehensive analysis
        risk_analysis = {"risk_level": result_label}
        management_type = risk_model.classify_management(risk_analysis)
        lifestyle_plan = lifestyle_gen.generate_plan(result_label, data, management_type)
        notification_schedule = scheduler.create_schedule(data['patient_id'], result_label)

        # Save assessment to database
        if db:
            db.save_assessment({
                'patient_id': data['patient_id'],
                'timestamp': datetime.datetime.now(),
                'risk_analysis': risk_analysis,
                'management_type': management_type,
                'lifestyle_plan': lifestyle_plan,
                'notification_schedule': notification_schedule,
                'lipid_values': {
                    'total_cholesterol': data.get('total_cholesterol'),
                    'ldl': data.get('ldl'),
                    'hdl': data.get('hdl'),
                    'triglycerides': data.get('triglycerides'),
                    'vldl': data.get('vldl'),
                    'non_hdl': data.get('non_hdl')
                }
            })

        return jsonify({
            'success': True,
            'risk_analysis': risk_analysis,
            'management_type': management_type,
            'lifestyle_plan': lifestyle_plan,
            'notification_schedule': notification_schedule
        })

    except Exception as e:
        print(f"\n❌ Analysis Error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': f'Analysis failed: {str(e)}'
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_complete():
    """Complete workflow: Upload image -> Extract values -> Analyze risk"""
    try:
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        file = request.files['file']
        
        if not allowed_file(file.filename):
            return jsonify({
                "success": False, 
                "error": "Invalid file type"
            }), 400

        # Get patient ID
        patient_id = request.form.get("patient_id", "unknown")

        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        print(f"\n🔍 Complete analysis for: {filepath}")

        # Step 1: Extract lipid values
        extracted_data = extract_lipid_values(filepath)
        
        if 'error' in extracted_data:
            return jsonify({
                "success": False,
                "error": extracted_data.get("error"),
                "raw_text": extracted_data.get("raw_text", "")
            }), 400

        # Step 2: Predict risk
        from ml_model.predict import predict_risk
        risk_level = predict_risk(
            float(extracted_data['total_cholesterol']),
            float(extracted_data['ldl']),
            float(extracted_data['hdl']),
            float(extracted_data['triglycerides'])
        )

        # Step 3: Generate recommendations
        risk_analysis = {"risk_level": risk_level}
        management_type = risk_model.classify_management(risk_analysis)
        
        data_with_patient = {**extracted_data, 'patient_id': patient_id}
        lifestyle_plan = lifestyle_gen.generate_plan(risk_level, data_with_patient, management_type)
        notification_schedule = scheduler.create_schedule(patient_id, risk_level)

        # Save to database
        if db:
            db.save_assessment({
                'patient_id': patient_id,
                'timestamp': datetime.datetime.now(),
                'risk_analysis': risk_analysis,
                'management_type': management_type,
                'lifestyle_plan': lifestyle_plan,
                'notification_schedule': notification_schedule,
                'extracted_data': extracted_data
            })

        return jsonify({
            'success': True,
            'extracted_data': extracted_data,
            'risk_analysis': risk_analysis,
            'management_type': management_type,
            'lifestyle_plan': lifestyle_plan,
            'notification_schedule': notification_schedule
        })

    except Exception as e:
        print(f"\n❌ Complete Analysis Error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500


@app.route('/api/patient-history/<patient_id>', methods=['GET'])
def get_patient_history(patient_id):
    """Get patient assessment history"""
    try:
        if db:
            history = db.get_patient_history(patient_id)
            return jsonify({
                'success': True,
                'patient_id': patient_id,
                'history': history
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Database not available'
            }), 503
    except Exception as e:
        print(f"\n❌ History Error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
def upload_file_api():
    """Handle file upload for manual analysis (matches frontend expectation)"""
    try:
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({
                "success": False, 
                "error": "Invalid file type. Only PNG, JPG, JPEG allowed"
            }), 400

        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        print(f"\n🔍 Processing uploaded file: {filepath}")

        # Extract lipid values using OCR
        extracted_data = extract_lipid_values(filepath)
        
        if 'error' in extracted_data:
            return jsonify({
                "success": False,
                "error": extracted_data.get("error", "OCR extraction failed"),
                "raw_text": extracted_data.get("raw_text", "")
            }), 400

        # Predict risk level
        from ml_model.predict import predict_risk
        risk_level = predict_risk(
            float(extracted_data.get('total_cholesterol', 200)),
            float(extracted_data.get('ldl', 130)),
            float(extracted_data.get('hdl', 50)),
            float(extracted_data.get('triglycerides', 150))
        )

        # Clean up file (optional)
        try:
            os.remove(filepath)
        except:
            pass

        # Return data in format expected by frontend
        return jsonify({
            'success': True,
            'total_cholesterol': extracted_data.get('total_cholesterol'),
            'ldl': extracted_data.get('ldl'),
            'hdl': extracted_data.get('hdl'),
            'triglycerides': extracted_data.get('triglycerides'),
            'vldl': extracted_data.get('vldl'),
            'non_hdl': extracted_data.get('non_hdl'),
            'risk_level': risk_level,
            'patient_name': extracted_data.get('patient_name', 'N/A'),
            'age': extracted_data.get('age', 'N/A'),
            'sex': extracted_data.get('sex', 'N/A'),
            'report_date': extracted_data.get('report_date', datetime.datetime.now().strftime('%Y-%m-%d'))
        }), 200

    except Exception as e:
        print(f"\n❌ Upload Error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': f"Server error: {str(e)}"
        }), 500


@app.route('/api/manual-entry', methods=['POST'])
def manual_entry_api():
    """Handle manual lipid value entry (matches frontend expectation)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['total_cholesterol', 'ldl', 'hdl', 'triglycerides']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False, 
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Predict risk level
        from ml_model.predict import predict_risk
        risk_level = predict_risk(
            float(data['total_cholesterol']),
            float(data['ldl']),
            float(data['hdl']),
            float(data['triglycerides'])
        )

        # Calculate derived values
        vldl = float(data['triglycerides']) / 5
        non_hdl = float(data['total_cholesterol']) - float(data['hdl'])

        return jsonify({
            'success': True,
            'total_cholesterol': data['total_cholesterol'],
            'ldl': data['ldl'],
            'hdl': data['hdl'],
            'triglycerides': data['triglycerides'],
            'vldl': round(vldl, 2),
            'non_hdl': round(non_hdl, 2),
            'risk_level': risk_level
        }), 200

    except Exception as e:
        print(f"\n❌ Manual Entry Error: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500


@app.route('/api/log-activity', methods=['POST'])
def log_daily_activity():
    """Log daily activities for adherence tracking"""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        date = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
        
        activities = {
            'diet_followed': data.get('diet_followed', 0),
            'exercise_completed': data.get('exercise_completed', 0),
            'medication_taken': data.get('medication_taken', 0),
            'water_intake_met': data.get('water_intake_met', 0),
            'sleep_quality': data.get('sleep_quality', 0),
            'stress_level': data.get('stress_level', 0),
            'notes': data.get('notes', '')
        }
        
        result = adherence_tracker.log_daily_activity(patient_id, date, activities)
        
        # Calculate current streak
        streak = adherence_tracker.get_current_streak(patient_id)
        
        return jsonify({
            'success': True,
            'message': 'Activity logged successfully',
            'current_streak': streak
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/adherence-score/<patient_id>', methods=['GET'])
def get_adherence_score(patient_id):
    """Get adherence score for a patient"""
    try:
        days = request.args.get('days', 30, type=int)
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        
        score = adherence_tracker.calculate_adherence_score(patient_id, start_date, end_date)
        streak = adherence_tracker.get_current_streak(patient_id)
        risk = adherence_tracker.predict_adherence_risk(patient_id, days)
        
        return jsonify({
            'success': True,
            'adherence_score': score,
            'current_streak': streak,
            'risk_analysis': risk
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/adherence-analytics/<patient_id>', methods=['GET'])
def get_adherence_analytics(patient_id):
    """Get detailed adherence analytics"""
    try:
        conn = sqlite3.connect('database/cardio_health.db')
        cursor = conn.cursor()
        
        # Get last 30 days of activity
        cursor.execute('''
            SELECT 
                activity_date,
                diet_followed,
                exercise_completed,
                medication_taken,
                water_intake_met,
                sleep_quality,
                stress_level
            FROM daily_activities
            WHERE patient_id = ?
            AND activity_date >= date('now', '-30 days')
            ORDER BY activity_date ASC
        ''', (patient_id,))
        
        activities = []
        for row in cursor.fetchall():
            activities.append({
                'date': row[0],
                'diet': row[1],
                'exercise': row[2],
                'medication': row[3],
                'water': row[4],
                'sleep': row[5],
                'stress': row[6],
                'completion': (row[1] + row[2] + row[3] + row[4]) / 4 * 100
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'activities': activities,
            'total_days': len(activities)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ------------------------
# ERROR HANDLERS
# ------------------------
@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'File too large. Maximum size is 16MB'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


# ------------------------
# START SERVER
# ------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("🏥 Lipid Profile Risk Assessment System")
    print("=" * 60)
    print("✅ Server Components:")
    print("   - OCR Engine: PaddleOCR")
    print("   - ML Model: Risk Classification")
    print("   - Database: Active" if db else "   - Database: Inactive")
    print("=" * 60)
    print("📍 Server running at: http://localhost:5000")
    print("📍 Health check: http://localhost:5000/api/health")
    print("=" * 60)
    
    # Run in development mode
    app.run(debug=True, port=5000, host='0.0.0.0')
