import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os

class AdherencePredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = 'models/adherence_model.pkl'
        
    def train_model(self, X, y):
        """
        Train adherence prediction model
        X: Features (adherence history, demographics, risk factors)
        y: Target (0: will drop off, 1: will continue)
        """
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        
        # Save model
        self.save_model()
        
        return self.model
    
    def predict_adherence(self, patient_data):
        """
        Predict adherence likelihood
        Returns: probability of continuing (0-1)
        """
        if self.model is None:
            self.load_model()
        
        # Extract features
        features = self._extract_features(patient_data)
        features_scaled = self.scaler.transform([features])
        
        # Predict
        probability = self.model.predict_proba(features_scaled)[0][1]
        
        return {
            'adherence_probability': probability,
            'risk_level': self._classify_risk(probability),
            'recommended_actions': self._get_recommendations(probability, patient_data)
        }
    
    def _extract_features(self, patient_data):
        """Extract relevant features for prediction"""
        return [
            patient_data.get('age', 45),
            patient_data.get('baseline_risk_score', 50),
            patient_data.get('days_since_diagnosis', 30),
            patient_data.get('avg_diet_score', 50),
            patient_data.get('avg_exercise_score', 50),
            patient_data.get('avg_medication_score', 50),
            patient_data.get('current_streak', 0),
            patient_data.get('total_active_days', 0),
            patient_data.get('missed_days_last_week', 0),
            patient_data.get('engagement_trend', 0)  # Positive or negative slope
        ]
    
    def _classify_risk(self, probability):
        """Classify dropout risk"""
        if probability >= 0.8:
            return "low"
        elif probability >= 0.6:
            return "medium"
        elif probability >= 0.4:
            return "high"
        else:
            return "very_high"
    
    def _get_recommendations(self, probability, patient_data):
        """Generate intervention recommendations"""
        recommendations = []
        
        if probability < 0.4:
            recommendations.append({
                'priority': 'urgent',
                'action': 'Schedule immediate counseling session',
                'reason': 'Very high dropout risk detected'
            })
            recommendations.append({
                'priority': 'urgent',
                'action': 'Contact patient via phone',
                'reason': 'Direct intervention needed'
            })
        
        if patient_data.get('avg_diet_score', 100) < 50:
            recommendations.append({
                'priority': 'high',
                'action': 'Provide simplified meal plans',
                'reason': 'Low diet adherence'
            })
        
        if patient_data.get('avg_exercise_score', 100) < 50:
            recommendations.append({
                'priority': 'high',
                'action': 'Suggest easier exercise alternatives',
                'reason': 'Low exercise completion'
            })
        
        if patient_data.get('current_streak', 0) == 0:
            recommendations.append({
                'priority': 'medium',
                'action': 'Send motivational message',
                'reason': 'No recent activity logged'
            })
        
        return recommendations
    
    def save_model(self):
        """Save trained model"""
        os.makedirs('models', exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler
            }, f)
    
    def load_model(self):
        """Load trained model"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']