import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (classification_report, confusion_matrix, roc_auc_score, 
                             accuracy_score, precision_recall_fscore_support, roc_curve)
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

class LipidRiskModelTrainer:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = None
        self.class_names = None
        
    def load_data(self, csv_path):
        """Load and prepare dataset"""
        print(f"📂 Loading data from {csv_path}...")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Dataset not found: {csv_path}")
        
        df = pd.read_csv(csv_path)
        
        print(f"✅ Loaded {len(df)} records")
        print(f"📊 Columns: {list(df.columns)}")
        
        return df
    
    def prepare_features(self, df):
        """Prepare features for training"""
        # Define feature columns
        feature_cols = [
            'age', 'bmi', 'smoking', 'diabetes', 'hypertension', 'family_history',
            'total_cholesterol', 'ldl', 'hdl', 'triglycerides',
            'vldl', 'non_hdl', 'tc_hdl_ratio', 'ldl_hdl_ratio', 'tg_hdl_ratio',
            'blood_glucose'
        ]
        
        # Check available features
        available_features = [col for col in feature_cols if col in df.columns]
        
        print(f"✅ Using {len(available_features)} features:")
        for feat in available_features:
            print(f"   • {feat}")
        
        self.feature_names = available_features
        
        X = df[available_features].copy()
        
        # Handle missing values
        X = X.fillna(X.median())
        
        # Encode target variable
        y = df['risk_level']
        
        print(f"\n🎯 Target Distribution:")
        print(y.value_counts())
        print(f"\nClass percentages:")
        for cls, count in y.value_counts().items():
            print(f"  {cls}: {count/len(y)*100:.1f}%")
        
        return X, y
    
    def train(self, X, y, test_size=0.2, cv_folds=5):
        """Train the model with comprehensive evaluation"""
        print("\n🎯 Starting model training...")
        print("=" * 60)
        
        # Split data with stratification
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"📊 Training set: {len(X_train)} samples")
        print(f"📊 Test set: {len(X_test)} samples")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Hyperparameter tuning with GridSearch
        print("\n🔍 Performing hyperparameter optimization...")
        
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4],
            'max_features': ['sqrt', 'log2', None]
        }
        
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        
        # Use StratifiedKFold for better cross-validation
        skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
        
        grid_search = GridSearchCV(
            rf, param_grid, cv=skf, scoring='accuracy', 
            n_jobs=-1, verbose=1, return_train_score=True
        )
        
        grid_search.fit(X_train_scaled, y_train)
        
        self.model = grid_search.best_estimator_
        self.class_names = self.model.classes_
        
        print(f"\n✅ Best parameters found:")
        for param, value in grid_search.best_params_.items():
            print(f"   {param}: {value}")
        
        # Cross-validation scores
        print(f"\n📊 Cross-Validation Results:")
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=skf, scoring='accuracy')
        print(f"   Mean CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        print(f"   Individual fold scores: {[f'{score:.4f}' for score in cv_scores]}")
        
        # Training set performance
        y_train_pred = self.model.predict(X_train_scaled)
        train_accuracy = accuracy_score(y_train, y_train_pred)
        
        # Test set performance
        y_test_pred = self.model.predict(X_test_scaled)
        test_accuracy = accuracy_score(y_test, y_test_pred)
        
        print(f"\n📈 Model Performance:")
        print(f"   Training Accuracy: {train_accuracy:.4f}")
        print(f"   Test Accuracy: {test_accuracy:.4f}")
        print(f"   Difference (overfitting check): {abs(train_accuracy - test_accuracy):.4f}")
        
        # Detailed classification report
        print(f"\n📋 Detailed Classification Report (Test Set):")
        print("=" * 60)
        print(classification_report(y_test, y_test_pred))
        
        # Per-class metrics
        precision, recall, f1, support = precision_recall_fscore_support(y_test, y_test_pred)
        print(f"\n📊 Per-Class Metrics:")
        for i, cls in enumerate(self.class_names):
            print(f"\n{cls}:")
            print(f"   Precision: {precision[i]:.4f}")
            print(f"   Recall: {recall[i]:.4f}")
            print(f"   F1-Score: {f1[i]:.4f}")
            print(f"   Support: {int(support[i])}")
        
        # Feature importance analysis
        self.analyze_feature_importance()
        
        # Generate visualizations
        self.plot_confusion_matrix(y_test, y_test_pred)
        self.plot_roc_curves(X_test_scaled, y_test)
        self.plot_learning_curves(X_train_scaled, y_train)
        
        return {
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'cv_scores': cv_scores,
            'best_params': grid_search.best_params_,
            'classification_report': classification_report(y_test, y_test_pred, output_dict=True)
        }
    
    def analyze_feature_importance(self):
        """Analyze and plot feature importance"""
        importances = self.model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        print(f"\n🔝 Top 10 Most Important Features:")
        for i in range(min(10, len(indices))):
            idx = indices[i]
            print(f"   {i+1}. {self.feature_names[idx]}: {importances[idx]:.4f}")
        
        # Plot feature importance
        plt.figure(figsize=(12, 8))
        plt.title("Feature Importance", fontsize=16, fontweight='bold')
        plt.bar(range(len(importances)), importances[indices], color='steelblue', alpha=0.8)
        plt.xticks(range(len(importances)), [self.feature_names[i] for i in indices], 
                   rotation=45, ha='right')
        plt.xlabel('Features', fontsize=12)
        plt.ylabel('Importance Score', fontsize=12)
        plt.tight_layout()
        plt.savefig('ml_model/feature_importance.png', dpi=300, bbox_inches='tight')
        print("✅ Feature importance plot saved: ml_model/feature_importance.png")
        plt.close()
    
    def plot_confusion_matrix(self, y_true, y_pred):
        """Plot confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=self.class_names, 
                    yticklabels=self.class_names,
                    cbar_kws={'label': 'Count'})
        plt.title('Confusion Matrix', fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        plt.savefig('ml_model/confusion_matrix.png', dpi=300, bbox_inches='tight')
        print("✅ Confusion matrix saved: ml_model/confusion_matrix.png")
        plt.close()
    
    def plot_roc_curves(self, X_test, y_test):
        """Plot ROC curves for multi-class classification"""
        from sklearn.preprocessing import label_binarize
        from sklearn.metrics import roc_curve, auc
        from itertools import cycle
        
        # Binarize the output
        y_test_bin = label_binarize(y_test, classes=self.class_names)
        n_classes = y_test_bin.shape[1]
        
        # Get probability predictions
        y_score = self.model.predict_proba(X_test)
        
        # Compute ROC curve and ROC area for each class
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        
        for i in range(n_classes):
            fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_score[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])
        
        # Plot
        plt.figure(figsize=(10, 8))
        colors = cycle(['blue', 'red', 'green'])
        
        for i, color in zip(range(n_classes), colors):
            plt.plot(fpr[i], tpr[i], color=color, lw=2,
                     label=f'{self.class_names[i]} (AUC = {roc_auc[i]:.2f})')
        
        plt.plot([0, 1], [0, 1], 'k--', lw=2, label='Random Classifier')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('ROC Curves - Multi-Class Classification', fontsize=16, fontweight='bold')
        plt.legend(loc="lower right", fontsize=10)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('ml_model/roc_curves.png', dpi=300, bbox_inches='tight')
        print("✅ ROC curves saved: ml_model/roc_curves.png")
        plt.close()
    
    def plot_learning_curves(self, X_train, y_train):
        """Plot learning curves to detect overfitting"""
        from sklearn.model_selection import learning_curve
        
        train_sizes, train_scores, val_scores = learning_curve(
            self.model, X_train, y_train, cv=5, n_jobs=-1,
            train_sizes=np.linspace(0.1, 1.0, 10), scoring='accuracy'
        )
        
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        val_mean = np.mean(val_scores, axis=1)
        val_std = np.std(val_scores, axis=1)
        
        plt.figure(figsize=(10, 6))
        plt.plot(train_sizes, train_mean, label='Training score', color='blue', marker='o')
        plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, 
                         alpha=0.15, color='blue')
        plt.plot(train_sizes, val_mean, label='Cross-validation score', color='red', marker='s')
        plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, 
                         alpha=0.15, color='red')
        plt.xlabel('Training Set Size', fontsize=12)
        plt.ylabel('Accuracy Score', fontsize=12)
        plt.title('Learning Curves', fontsize=16, fontweight='bold')
        plt.legend(loc='best', fontsize=10)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig('ml_model/learning_curves.png', dpi=300, bbox_inches='tight')
        print("✅ Learning curves saved: ml_model/learning_curves.png")
        plt.close()
    
    def save_model(self):
        """Save trained model and preprocessing objects"""
        os.makedirs('ml_model', exist_ok=True)
        
        joblib.dump(self.model, 'ml_model/lipid_risk_model.pkl')
        joblib.dump(self.scaler, 'ml_model/scaler.pkl')
        joblib.dump(self.feature_names, 'ml_model/feature_names.pkl')
        
        print(f"\n💾 Model Artifacts Saved:")
        print(f"   ✅ ml_model/lipid_risk_model.pkl")
        print(f"   ✅ ml_model/scaler.pkl")
        print(f"   ✅ ml_model/feature_names.pkl")


if __name__ == "__main__":
    print("=" * 60)
    print("🧠 LIPID PROFILE RISK ASSESSMENT - MODEL TRAINING")
    print("=" * 60)
    
    # Initialize trainer
    trainer = LipidRiskModelTrainer()
    
    # Load data
    dataset_path = "lipid_profile_dataset.csv"
    
    try:
        df = trainer.load_data(dataset_path)
        
        # Prepare features
        X, y = trainer.prepare_features(df)
        
        # Train model
        metrics = trainer.train(X, y)
        
        # Save model
        trainer.save_model()
        
        print("\n" + "=" * 60)
        print("🎉 TRAINING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\n📊 Final Metrics:")
        print(f"   Test Accuracy: {metrics['test_accuracy']:.4f}")
        print(f"   CV Mean Accuracy: {metrics['cv_scores'].mean():.4f}")
        print(f"\n✅ Model is ready for deployment!")
        
    except FileNotFoundError:
        print(f"\n❌ Error: Dataset not found at '{dataset_path}'")
        print("💡 Please run 'python generate_dataset.py' first to create the dataset.")
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()