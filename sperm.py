from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
import joblib
import json
import os
from sklearn.metrics.pairwise import cosine_similarity

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load data once
FOOD_PATH = os.path.join(os.path.dirname(__file__), "nepalifood.csv")
USERS_PATH = os.path.join(os.path.dirname(__file__), "user_profiles_no_score.json")
# MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/sperm_health_model.joblib")
# SCALER_PATH = os.path.join(os.path.dirname(__file__), "../models/sperm_health_scaler.joblib")

MODEL_PATH = os.path.join(BASE_DIR, "model", "sperm_health_model.joblib")
SCALER_PATH = os.path.join(BASE_DIR, "model", "sperm_health_scaler.joblib")

food_df = pd.read_csv(FOOD_PATH)
with open(USERS_PATH) as f:
    user_profiles = json.load(f)
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

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

class MealLog(BaseModel):
    food_name: str
    amount_grams: float

class RecommendationRequest(BaseModel):
    user_id: str
    meals: List[MealLog]

@router.post("/sperm-recommendation")
def sperm_food_recommendation(request: RecommendationRequest):
    user = next((u for u in user_profiles if u["user_id"] == request.user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. Predict sperm health score
    diet_encoding = {"unhealthy": 0, "average": 1, "healthy": 2}
    input_data = np.array([[user["age"],
                            int(user["smoker"]),
                            diet_encoding[user["diet"]],
                            int(user["exercise"]),
                            user["sleep_hours"],
                            user["bmi"]]])
    input_scaled = scaler.transform(input_data)
    sperm_score = round(model.predict(input_scaled)[0], 2)

    # 2. Calculate nutrient intake
    intake = {nut: 0 for nut in nutrients}
    for entry in request.meals:
        match = food_df[food_df["food_name"].str.lower() == entry.food_name.lower()]
        if not match.empty:
            for nut in nutrients:
                intake[nut] += (match[nut].values[0] * entry.amount_grams / 100)

    # 3. Calculate gaps
    multiplier = 1.0 if sperm_score >= 80 else 1.2
    gaps = {
        nut: max(0, nutrient_targets[nut] * multiplier - intake.get(nut, 0))
        for nut in nutrients
    }

    # 4. Recommend foods
    user_vector = np.array([gaps[nut] for nut in nutrients])
    if np.linalg.norm(user_vector) == 0:
        recommendations = food_df.sample(5)[["food_name", "region"]].to_dict(orient="records")
    else:
        user_vec_norm = user_vector / np.linalg.norm(user_vector)
        food_vectors = food_df[nutrients].fillna(0).values
        food_vectors_norm = food_vectors / np.linalg.norm(food_vectors, axis=1, keepdims=True)
        food_df["similarity"] = cosine_similarity([user_vec_norm], food_vectors_norm)[0]
        recommendations = food_df.sort_values(by="similarity", ascending=False)\
                                 .head(5)[["food_name", "similarity"]].to_dict(orient="records")

    return {
        "sperm_health_score": sperm_score,
        "nutrient_intake": intake,
        "nutrient_gaps": gaps,
        "recommendations": recommendations
    }
