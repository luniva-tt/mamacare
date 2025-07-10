import pandas as pd
import numpy as np
import joblib
import json
from sklearn.metrics.pairwise import cosine_similarity


food_df = pd.read_csv("nepalifood.csv")
with open("user_profiles_no_score.json") as f:
    user_profiles = json.load(f)

model = joblib.load("sperm_health_model.pkl")
scaler = joblib.load("sperm_health_scaler.pkl")


nutrients = ['vitaminC', 'vitaminA', 'folate', 'iron', 'calcium', 'protein', 'fat']
nutrient_targets = {
    'vitaminC': 90,
    'vitaminA': 900,
    'folate': 400,
    'iron': 8,
    'calcium': 1000,
    'protein': 56,
    'fat': 60
}

# ====== FUNCTIONS ======

def predict_sperm_health_score(profile):
    diet_encoding = {"unhealthy": 0, "average": 1, "healthy": 2}
    input_data = np.array([[
        profile["age"],
        int(profile["smoker"]),
        diet_encoding[profile["diet"]],
        int(profile["exercise"]),
        profile["sleep_hours"],
        profile["bmi"]
    ]])
    input_scaled = scaler.transform(input_data)
    return round(model.predict(input_scaled)[0], 2)

def get_nutrient_intake(logs, food_df):
    intake = {nut: 0 for nut in nutrients}
    for entry in logs:
        match = food_df[food_df["food_name"].str.lower() == entry["food_name"].lower()]
        if not match.empty:
            for nut in nutrients:
                intake[nut] += (match[nut].values[0] * entry["amount_grams"] / 100)
    return intake

def calculate_gaps(intake, targets, sperm_score):
    multiplier = 1.0 if sperm_score >= 80 else 1.2  # if sperm score is low, boost target
    return {nut: max(0, targets[nut] * multiplier - intake.get(nut, 0)) for nut in nutrients}

def recommend_foods_from_gaps(gaps, food_df, top_n=5):
    user_vector = np.array([gaps[nut] for nut in nutrients])
    if np.linalg.norm(user_vector) == 0:
        return food_df.sample(top_n)[["food_name", "region"]]

    user_vec_norm = user_vector / np.linalg.norm(user_vector)
    food_vectors = food_df[nutrients].fillna(0).values
    food_vectors_norm = food_vectors / np.linalg.norm(food_vectors, axis=1, keepdims=True)
    food_df["similarity"] = cosine_similarity([user_vec_norm], food_vectors_norm)[0]
    return food_df.sort_values(by="similarity", ascending=False).head(top_n)[["food_name", "region", "similarity"]]

# ====== DEMO EXECUTION ======
if __name__ == "__main__":
    # Pick a user
    user = user_profiles[1]

    # Logged meals (must be from nepalifood.csv)
    logged_meals = [
        {"food_name": "Spinach", "amount_grams": 100},
        {"food_name": "Tomato", "amount_grams": 50}
    ]

    # Run pipeline
    sperm_score = predict_sperm_health_score(user)
    intake = get_nutrient_intake(logged_meals, food_df)
    gaps = calculate_gaps(intake, nutrient_targets, sperm_score)
    top_foods = recommend_foods_from_gaps(gaps, food_df)


import joblib

# Save the trained model
joblib.dump(model, 'sperm_health_model.joblib')

# Save the feature scaler
joblib.dump(scaler, 'sperm_health_scaler.joblib')

print("✅ Model and scaler saved as .joblib files.")

