import joblib
import pandas as pd

class ComplicationPredictor:
    def __init__(self, model_path, encoder_path, target_encoder_path):
        self.model = joblib.load(model_path)
        self.encoders = joblib.load(encoder_path)
        self.target_encoder = joblib.load(target_encoder_path)

    def predict(self, symptoms: dict):
        df = pd.DataFrame([symptoms])

        # Apply label encoders to categorical columns
        for col in self.encoders:
            df[col] = self.encoders[col].transform(df[col])

        prediction = self.model.predict(df)[0]
        condition = self.target_encoder.inverse_transform([prediction])[0]
        return condition
