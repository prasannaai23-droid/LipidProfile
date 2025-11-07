import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

class RiskClassifier:
    def __init__(self):
        # Load pre-trained model or train new one
        try:
            self.model = joblib.load('ml_model/trained_model.pkl')
        except:
            self.model = self._train_initial_model()
    
    def classify_risk(self, patient_data):
        """
        Classify patient risk based on lipid profile and other factors
        Returns: {
            'risk_level': 'urgent'|'high'|'medium'|'low',
            'risk_score': float,
            'critical_factors': list,
            'interpretation': str
        }
        """
        # Extract features
        features = self._extract_features(patient_data)
        
        # Calculate risk metrics
        ldl_risk = self._assess_ldl(patient_data['ldl'])
        hdl_risk = self._assess_hdl(patient_data['hdl'])
        triglyceride_risk = self._assess_triglycerides(patient_data['triglycerides'])
        glucose_risk = self._assess_glucose(patient_data['blood_glucose'])
        
        # ASCVD Risk Score (simplified)
        ascvd_score = self._calculate_ascvd_risk(patient_data)
        
        # Determine risk level
        risk_score = (ldl_risk + hdl_risk + triglyceride_risk + 
                     glucose_risk + ascvd_score) / 5
        
        if risk_score >= 0.8 or patient_data.get('chest_pain') or patient_data['ldl'] > 190:
            risk_level = 'urgent'
            interpretation = self._generate_urgent_interpretation(patient_data)
        elif risk_score >= 0.6:
            risk_level = 'high'
            interpretation = self._generate_high_interpretation(patient_data)
        elif risk_score >= 0.4:
            risk_level = 'medium'
            interpretation = self._generate_medium_interpretation(patient_data)
        else:
            risk_level = 'low'
            interpretation = self._generate_low_interpretation(patient_data)
        
        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 2),
            'critical_factors': self._identify_critical_factors(patient_data),
            'interpretation': interpretation,
            'ldl_status': self._get_ldl_category(patient_data['ldl']),
            'hdl_status': self._get_hdl_category(patient_data['hdl'], patient_data['gender']),
            'triglyceride_status': self._get_trig_category(patient_data['triglycerides']),
            'atherosclerosis_risk': self._assess_atherosclerosis_risk(patient_data)
        }
    
    def classify_management(self, risk_analysis):
        """
        Determine if patient needs medical management or lifestyle modification
        """
        risk_level = risk_analysis['risk_level']
        
        if risk_level == 'urgent':
            return {
                'primary': 'medical_management',
                'requires_statin': True,
                'requires_immediate_consultation': True,
                'lifestyle_support': True,
                'message': 'URGENT: Immediate medical intervention required along with intensive lifestyle modification.'
            }
        elif risk_level == 'high':
            return {
                'primary': 'medical_management',
                'requires_statin': True,
                'requires_immediate_consultation': False,
                'lifestyle_support': True,
                'message': 'Medical management recommended. Statin therapy likely needed along with lifestyle changes.'
            }
        elif risk_level == 'medium':
            return {
                'primary': 'lifestyle_modification',
                'requires_statin': False,
                'requires_immediate_consultation': False,
                'lifestyle_support': True,
                'monitor_period': '3_months',
                'message': 'Lifestyle modification is primary approach. Medical review in 3 months.'
            }
        else:
            return {
                'primary': 'lifestyle_modification',
                'requires_statin': False,
                'requires_immediate_consultation': False,
                'lifestyle_support': True,
                'monitor_period': '6_months',
                'message': 'Maintain healthy lifestyle. Routine monitoring recommended.'
            }
    
    def _assess_ldl(self, ldl):
        """LDL-C risk assessment"""
        if ldl < 100: return 0.2
        elif ldl < 130: return 0.4
        elif ldl < 160: return 0.6
        elif ldl < 190: return 0.8
        else: return 1.0
    
    def _assess_hdl(self, hdl):
        """HDL-C risk assessment (inverse relationship)"""
        if hdl >= 60: return 0.2
        elif hdl >= 40: return 0.4
        else: return 0.8
    
    def _assess_triglycerides(self, trig):
        """Triglyceride risk assessment"""
        if trig < 150: return 0.2
        elif trig < 200: return 0.5
        elif trig < 500: return 0.8
        else: return 1.0
    
    def _assess_glucose(self, glucose):
        """Blood glucose risk assessment"""
        if glucose < 100: return 0.2
        elif glucose < 126: return 0.5  # Pre-diabetes
        else: return 0.8  # Diabetes
    
    def _calculate_ascvd_risk(self, data):
        """Simplified ASCVD risk calculation"""
        score = 0
        if data['age'] > 55: score += 0.3
        if data['smoking']: score += 0.2
        if data['family_history']: score += 0.2
        if data.get('bmi', 25) > 30: score += 0.15
        if 'hypertension' in data.get('existing_conditions', []): score += 0.15
        return min(score, 1.0)
    
    def _identify_critical_factors(self, data):
        factors = []
        if data['ldl'] > 160:
            factors.append('Dangerously high LDL cholesterol - major atherosclerosis risk')
        if data['hdl'] < 40:
            factors.append('Low HDL - reduced cardiovascular protection')
        if data['triglycerides'] > 200:
            factors.append('Elevated triglycerides - increased heart disease risk')
        if data['blood_glucose'] > 126:
            factors.append('Diabetic range glucose - accelerates plaque formation')
        if data['smoking']:
            factors.append('Smoking damages blood vessels and accelerates atherosclerosis')
        return factors
    
    def _assess_atherosclerosis_risk(self, data):
        """Assess risk of atherosclerosis development"""
        risk_factors = 0
        if data['ldl'] > 130: risk_factors += 2
        if data['hdl'] < 40: risk_factors += 1
        if data['smoking']: risk_factors += 2
        if data.get('bmi', 25) > 30: risk_factors += 1
        if data['blood_glucose'] > 100: risk_factors += 1
        
        if risk_factors >= 5:
            return 'High risk of plaque buildup and arterial narrowing. Immediate action required.'
        elif risk_factors >= 3:
            return 'Moderate atherosclerosis risk. Lifestyle changes crucial to prevent progression.'
        else:
            return 'Lower risk. Maintain healthy habits to prevent plaque development.'
    
    def _generate_urgent_interpretation(self, data):
        return f"""
        🚨 URGENT MEDICAL ATTENTION REQUIRED
        
        Your lipid profile indicates severe cardiovascular risk:
        • LDL Cholesterol: {data['ldl']} mg/dL (Extremely High)
        • Risk of acute cardiac events is significantly elevated
        
        ATHEROSCLEROSIS CONCERN:
        At these levels, cholesterol plaque rapidly accumulates in arteries,
        narrowing blood flow to heart and brain. This increases risk of:
        - Heart attack (myocardial infarction)
        - Stroke
        - Peripheral artery disease
        
        IMMEDIATE ACTIONS:
        1. Contact your physician within 24 hours
        2. Do NOT delay - this requires urgent medical evaluation
        3. Statin therapy likely needed immediately
        4. Intensive lifestyle modification essential
        
        ⚠️ This is a medical emergency-level finding.
        """
    
    def _generate_high_interpretation(self, data):
        return f"""
        ⚠️ HIGH CARDIOVASCULAR RISK DETECTED
        
        Your lipid levels indicate significant atherosclerotic risk:
        • LDL: {data['ldl']} mg/dL | HDL: {data['hdl']} mg/dL | 
        • Triglycerides: {data['triglycerides']} mg/dL
        
        ATHEROSCLEROSIS RISK:
        Cholesterol is depositing in arterial walls, forming plaques that:
        - Narrow arteries (reducing blood flow)
        - Can rupture causing blood clots
        - Lead to heart attack or stroke
        
        RECOMMENDED ACTIONS:
        1. Schedule physician appointment within 1-2 weeks
        2. Medical therapy (likely statins) recommended
        3. Aggressive lifestyle modification needed
        4. Regular monitoring essential
        
        Early intervention prevents irreversible arterial damage.
        """
    
    def _generate_medium_interpretation(self, data):
        return f"""
        ⚡ MODERATE RISK - ACTION NEEDED
        
        Your lipid profile shows concerning trends:
        • LDL: {data['ldl']} mg/dL (Above optimal)
        • Early atherosclerosis risk present
        
        UNDERSTANDING YOUR RISK:
        While not immediately dangerous, these levels promote gradual
        plaque buildup in arteries. Over time, this leads to:
        - Hardening of arteries (atherosclerosis)
        - Reduced circulation
        - Increased heart disease risk
        
        PREVENTION STRATEGY:
        1. Intensive lifestyle modification (diet, exercise)
        2. Medical review in 3 months
        3. Re-test lipids to assess response
        4. Medication may be needed if no improvement
        
        Acting now prevents future cardiovascular disease.
        """
    
    def _generate_low_interpretation(self, data):
        return f"""
        ✅ HEALTHY LIPID PROFILE
        
        Your levels are in healthy range:
        • LDL: {data['ldl']} mg/dL (Optimal)
        • HDL: {data['hdl']} mg/dL (Protective)
        
        CONTINUE HEART-HEALTHY HABITS:
        - Balanced Mediterranean-style diet
        - Regular physical activity
        - Maintain healthy weight
        - Avoid smoking
        
        Routine monitoring recommended every 6-12 months.
        """
    
    def _get_ldl_category(self, ldl):
        if ldl < 100: return 'Optimal'
        elif ldl < 130: return 'Near Optimal'
        elif ldl < 160: return 'Borderline High'
        elif ldl < 190: return 'High'
        else: return 'Very High'
    
    def _get_hdl_category(self, hdl, gender):
        if hdl >= 60: return 'Optimal (Protective)'
        elif hdl >= 40: return 'Acceptable'
        else: return 'Low (Risk Factor)'
    
    def _get_trig_category(self, trig):
        if trig < 150: return 'Normal'
        elif trig < 200: return 'Borderline High'
        elif trig < 500: return 'High'
        else: return 'Very High'
    
    def _extract_features(self, data):
        """Extract features for ML model"""
        return np.array([
            data['ldl'],
            data['hdl'],
            data['triglycerides'],
            data['blood_glucose'],
            data['age'],
            1 if data['gender'] == 'male' else 0,
            data.get('bmi', 25),
            1 if data['smoking'] else 0,
            1 if data['family_history'] else 0
        ]).reshape(1, -1)
    
    def _train_initial_model(self):
        """Train initial model - replace with actual training data"""
        # This is a placeholder - use real clinical data
        model = RandomForestClassifier(n_estimators=100)
        # model.fit(X_train, y_train)
        return model