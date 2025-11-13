import joblib
import numpy as np
import os

class LipidRiskPredictor:
    def __init__(self):
        model_dir = os.path.dirname(__file__)
        self.model = joblib.load(os.path.join(model_dir, 'lipid_risk_model.pkl'))
        self.scaler = joblib.load(os.path.join(model_dir, 'scaler.pkl'))
        self.feature_names = joblib.load(os.path.join(model_dir, 'feature_names.pkl'))
    
    def predict(self, lipid_values):
        """
        Predict risk level from lipid values
        
        Args:
            lipid_values: dict with keys: total_cholesterol, ldl, hdl, triglycerides, etc.
        
        Returns:
            dict with prediction, probability, and explanation
        """
        # Calculate derived features if missing
        if 'tc_hdl_ratio' not in lipid_values:
            lipid_values['tc_hdl_ratio'] = lipid_values['total_cholesterol'] / lipid_values['hdl']
        
        if 'ldl_hdl_ratio' not in lipid_values:
            lipid_values['ldl_hdl_ratio'] = lipid_values['ldl'] / lipid_values['hdl']
        
        if 'tg_hdl_ratio' not in lipid_values:
            lipid_values['tg_hdl_ratio'] = lipid_values['triglycerides'] / lipid_values['hdl']
        
        if 'vldl' not in lipid_values:
            lipid_values['vldl'] = lipid_values['triglycerides'] / 5
        
        if 'non_hdl' not in lipid_values:
            lipid_values['non_hdl'] = lipid_values['total_cholesterol'] - lipid_values['hdl']
        
        # Prepare features in correct order
        features = [lipid_values.get(f, 0) for f in self.feature_names]
        features_array = np.array(features).reshape(1, -1)
        
        # Scale features
        features_scaled = self.scaler.transform(features_array)
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        # Get class probabilities
        classes = self.model.classes_
        prob_dict = {cls: float(prob) for cls, prob in zip(classes, probabilities)}
        
        return {
            'risk_level': prediction,
            'confidence': float(max(probabilities)),
            'probabilities': prob_dict,
            'feature_importance': self._get_feature_contributions(features_array)
        }
    
    def _get_feature_contributions(self, features):
        """Calculate which features contributed most to the prediction"""
        importances = self.model.feature_importances_
        contributions = {}
        
        for i, (name, importance) in enumerate(zip(self.feature_names, importances)):
            contributions[name] = {
                'value': float(features[0][i]),
                'importance': float(importance)
            }
        
        return contributions


# Convenience function for backward compatibility
def predict_risk(total_cholesterol, ldl, hdl, triglycerides):
    """Simple prediction function"""
    predictor = LipidRiskPredictor()
    result = predictor.predict({
        'total_cholesterol': total_cholesterol,
        'ldl': ldl,
        'hdl': hdl,
        'triglycerides': triglycerides
    })
    return result['risk_level']
