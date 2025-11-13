# Machine Learning Model Project

This project is a machine learning application that allows users to train a model and make predictions through a web interface. The application is built using Python for the backend and HTML, CSS, and JavaScript for the frontend.

## Project Structure

```
ml-model-project
├── src
│   ├── model
│   │   ├── train.py        # Contains functions and classes for training the machine learning model.
│   │   └── predict.py      # Includes functions for making predictions with the trained model.
│   ├── data
│   │   └── preprocessing.py # Handles data preprocessing tasks.
│   └── app.py              # Main application entry point that sets up the web server.
├── static
│   ├── css
│   │   └── style.css       # CSS styles for the web application.
│   └── js
│       └── script.js       # JavaScript code for client-side functionality.
├── templates
│   └── index.html          # Main HTML template for the web application.
├── requirements.txt        # Lists the Python dependencies required for the project.
└── README.md               # Documentation for the project.
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd ml-model-project
   ```

2. **Install dependencies**:
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   Start the Flask application by running:
   ```
   python src/app.py
   ```
   The application will be accessible at `http://127.0.0.1:5000`.

## Usage

- Navigate to the web application in your browser.
- Use the provided forms to input data for training the model and making predictions.
- Results will be displayed on the same page.

## Additional Information

- Ensure that you have all the necessary libraries installed as specified in `requirements.txt`.
- Modify the model training and prediction logic in `src/model/train.py` and `src/model/predict.py` as needed for your specific use case.
# 🏥 AI-Powered Lipid Profile Risk Assessment System

This project is a Machine Learning + Flask-based web application designed for automated cardiovascular risk screening using lipid profile reports.

The system analyzes:
- LDL (Low-Density Lipoprotein)
- HDL (High-Density Lipoprotein)
- Triglycerides
- Total Cholesterol
- Blood Glucose & Risk Factors

It classifies the patient risk into ✅ Low / ⚠ Medium / 🔴 High / 🚨 Urgent categories and generates:
✔ Personalized lifestyle recommendations  
✔ Medical management guidance  
✔ Follow-up notification scheduling  
✔ Adherence tracking with escalation alerts  

---

## ✨ Key Features

| Feature | Description |
|--------|-------------|
| 🧠 ML-Based Risk Classifier | Predicts cardiovascular risk from lab values |
| 🍎 Lifestyle Plan Generator | Daily exercise, diet, and precautions |
| ⏰ Notification Scheduler | Sends reminders based on risk level |
| 📊 Patient Dashboard | History, trends, adherence logs |
| 🛑 Intelligent Escalation | Alerts clinician for poor adherence |
| 🔐 Secure Storage | Local database tracking patients |

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask, SQLite |
| Frontend | HTML, CSS, JavaScript |
| AI/ML | Scikit-Learn Model |
| Deployment | Localhost / Cloud-ready |

---

## 📁 Folder Structure

