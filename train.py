from recommender import NutrientGapRecommender
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "nepalifood.csv")

model = NutrientGapRecommender(csv_path)
joblib.dump(model, os.path.join(BASE_DIR, "model", "recommender_model.joblib"))

# Save model into model/ folder
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/recommender_model.joblib")
