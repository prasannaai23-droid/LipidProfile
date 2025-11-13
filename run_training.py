import os
import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    print(f"📦 Installing {package}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
    print(f"✅ {package} installed")

def check_dependencies():
    """Check and install required packages"""
    required = ['seaborn', 'matplotlib', 'scikit-learn', 'pandas', 'numpy', 'joblib']
    
    print("🔍 Checking dependencies...\n")
    
    for package in required:
        try:
            if package == 'scikit-learn':
                __import__('sklearn')
            else:
                __import__(package)
            print(f"✅ {package} already installed")
        except ImportError:
            install_package(package)
    
    print("\n" + "="*60 + "\n")

print("🚀 Starting Complete ML Pipeline...\n")

# Step 0: Check dependencies
check_dependencies()

# Step 1: Generate dataset
print("Step 1: Generating dataset...")
subprocess.run([sys.executable, "generate_dataset.py"], check=True)

print("\n" + "="*60 + "\n")

# Step 2: Train model
print("Step 2: Training model...")
subprocess.run([sys.executable, "ml_model/train_model.py"], check=True)

print("\n" + "="*60)
print("✅ Pipeline completed successfully!")
print("="*60)