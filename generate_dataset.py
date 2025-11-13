import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

def generate_realistic_lipid_dataset(n_samples=500):
    """
    Generate realistic lipid profile dataset based on medical guidelines
    """
    
    data = []
    
    for i in range(n_samples):
        # Patient demographics
        age = np.random.randint(25, 85)
        gender = random.choice(['M', 'F'])
        bmi = np.random.normal(27, 5)
        bmi = max(18, min(40, bmi))  # Constrain BMI
        
        # Risk factors (probabilities increase with age)
        smoking = random.random() < (0.2 + age * 0.002)
        diabetes = random.random() < (0.1 + age * 0.003)
        hypertension = random.random() < (0.15 + age * 0.004)
        family_history = random.random() < 0.3
        
        # Baseline lipid values (influenced by demographics and risk factors)
        age_factor = (age - 25) / 60  # Normalize age effect
        risk_factor = sum([smoking, diabetes, hypertension, family_history]) * 0.15
        
        # Total Cholesterol (normal: 125-200, borderline: 200-239, high: ≥240)
        tc_base = np.random.normal(190, 40)
        tc_adjustment = age_factor * 30 + risk_factor * 50 + (bmi - 25) * 2
        total_cholesterol = tc_base + tc_adjustment
        total_cholesterol = max(120, min(400, total_cholesterol))
        
        # LDL Cholesterol (optimal: <100, near optimal: 100-129, borderline high: 130-159, high: ≥160)
        ldl_base = np.random.normal(115, 35)
        ldl_adjustment = age_factor * 25 + risk_factor * 45 + (bmi - 25) * 1.8
        ldl = ldl_base + ldl_adjustment
        ldl = max(40, min(250, ldl))
        
        # HDL Cholesterol (low: <40 for men, <50 for women; high: ≥60)
        hdl_base = 55 if gender == 'M' else 60
        hdl_noise = np.random.normal(0, 12)
        hdl_adjustment = -age_factor * 8 - risk_factor * 10 - (bmi - 25) * 0.8
        hdl = hdl_base + hdl_noise + hdl_adjustment
        hdl = max(25, min(100, hdl))
        
        # Triglycerides (normal: <150, borderline high: 150-199, high: ≥200)
        tg_base = np.random.normal(130, 50)
        tg_adjustment = age_factor * 20 + risk_factor * 60 + (bmi - 25) * 3
        triglycerides = tg_base + tg_adjustment
        triglycerides = max(50, min(500, triglycerides))
        
        # Calculate derived values
        vldl = triglycerides / 5
        non_hdl = total_cholesterol - hdl
        tc_hdl_ratio = total_cholesterol / hdl if hdl > 0 else 0
        ldl_hdl_ratio = ldl / hdl if hdl > 0 else 0
        tg_hdl_ratio = triglycerides / hdl if hdl > 0 else 0
        
        # Determine risk level based on multiple factors
        risk_score = 0
        
        # LDL contribution
        if ldl >= 190: risk_score += 3
        elif ldl >= 160: risk_score += 2
        elif ldl >= 130: risk_score += 1
        
        # HDL contribution
        if hdl < 40: risk_score += 2
        elif hdl >= 60: risk_score -= 1
        
        # Triglycerides contribution
        if triglycerides >= 200: risk_score += 2
        elif triglycerides >= 150: risk_score += 1
        
        # Total cholesterol contribution
        if total_cholesterol >= 240: risk_score += 2
        elif total_cholesterol >= 200: risk_score += 1
        
        # Ratio contribution
        if tc_hdl_ratio >= 5: risk_score += 1
        if ldl_hdl_ratio >= 3.5: risk_score += 1
        
        # Risk factors contribution
        if smoking: risk_score += 1
        if diabetes: risk_score += 2
        if hypertension: risk_score += 1
        if family_history: risk_score += 1
        if age >= 65: risk_score += 1
        if bmi >= 30: risk_score += 1
        
        # Classify risk level
        if risk_score >= 8:
            risk_level = 'High Risk'
        elif risk_score >= 4:
            risk_level = 'Moderate Risk'
        else:
            risk_level = 'Low Risk'
        
        # Blood glucose (influenced by diabetes status)
        if diabetes:
            blood_glucose = np.random.normal(160, 40)
        else:
            blood_glucose = np.random.normal(95, 15)
        blood_glucose = max(60, min(400, blood_glucose))
        
        # Generate report date
        days_ago = random.randint(0, 365)
        report_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # Create patient record
        patient = {
            'patient_id': f'PT{str(i+1).zfill(4)}',
            'patient_name': f'Patient_{i+1}',
            'age': int(age),
            'gender': gender,
            'bmi': round(bmi, 1),
            'smoking': int(smoking),
            'diabetes': int(diabetes),
            'hypertension': int(hypertension),
            'family_history': int(family_history),
            'total_cholesterol': round(total_cholesterol, 1),
            'ldl': round(ldl, 1),
            'hdl': round(hdl, 1),
            'triglycerides': round(triglycerides, 1),
            'vldl': round(vldl, 1),
            'non_hdl': round(non_hdl, 1),
            'tc_hdl_ratio': round(tc_hdl_ratio, 2),
            'ldl_hdl_ratio': round(ldl_hdl_ratio, 2),
            'tg_hdl_ratio': round(tg_hdl_ratio, 2),
            'blood_glucose': round(blood_glucose, 1),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'report_date': report_date
        }
        
        data.append(patient)
    
    df = pd.DataFrame(data)
    return df


if __name__ == "__main__":
    print("🔬 Generating 500-sample lipid profile dataset...")
    
    # Generate dataset
    df = generate_realistic_lipid_dataset(500)
    
    # Save to CSV
    output_path = 'lipid_profile_dataset.csv'
    df.to_csv(output_path, index=False)
    
    print(f"✅ Dataset saved to: {output_path}")
    print(f"\n📊 Dataset Summary:")
    print(f"Total samples: {len(df)}")
    print(f"\n🎯 Risk Level Distribution:")
    print(df['risk_level'].value_counts())
    print(f"\n👥 Gender Distribution:")
    print(df['gender'].value_counts())
    print(f"\n📈 Age Statistics:")
    print(df['age'].describe())
    print(f"\n💊 Lipid Values (Mean ± Std):")
    print(f"Total Cholesterol: {df['total_cholesterol'].mean():.1f} ± {df['total_cholesterol'].std():.1f}")
    print(f"LDL: {df['ldl'].mean():.1f} ± {df['ldl'].std():.1f}")
    print(f"HDL: {df['hdl'].mean():.1f} ± {df['hdl'].std():.1f}")
    print(f"Triglycerides: {df['triglycerides'].mean():.1f} ± {df['triglycerides'].std():.1f}")
    
    # Show first few rows
    print(f"\n📋 Sample Data (first 5 rows):")
    print(df.head())
    
    # Show class balance
    print(f"\n⚖️ Class Balance:")
    for risk in df['risk_level'].unique():
        count = len(df[df['risk_level'] == risk])
        percentage = (count / len(df)) * 100
        print(f"{risk}: {count} ({percentage:.1f}%)")