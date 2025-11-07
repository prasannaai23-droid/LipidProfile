class ModelPredictor:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = None

    def load_model(self):
        import joblib
        self.model = joblib.load(self.model_path)

    def make_prediction(self, input_data):
        if self.model is None:
            raise Exception("Model is not loaded. Please load the model before making predictions.")
        return self.model.predict(input_data)