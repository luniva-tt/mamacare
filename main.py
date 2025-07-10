from fastapi import FastAPI, Body
from pydantic import BaseModel

from fastapi import Query
from typing import List
import joblib
import pandas as pd
import os

from recommender import NutrientGapRecommender
from complication_model import ComplicationPredictor
from articles import router as articles_router
from foodrecommendation import router as recommendations
from meals import router as meals_router
from nutritionintake import router as intake_router

from recipes import router as recipes_router
from sperm import router as sperm_router

app = FastAPI()

# ==== Load Models ====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
recommender = joblib.load(os.path.join(BASE_DIR, "model", "recommender_model.joblib"))


complication_model = ComplicationPredictor(
    os.path.join(BASE_DIR, "model", "pregnancy_model.joblib"),
    os.path.join(BASE_DIR, "model", "label_encoders.joblib"),
    os.path.join(BASE_DIR, "model", "target_encoder.joblib"),
)
app = FastAPI()

# ==== Recommender Input ====
class RecommendationRequest(BaseModel):
    user_region: str
    food_names: List[str]
    top_n: int = 5

@app.post("/recommend")
def recommend_food(data: RecommendationRequest):
    result = recommender.recommend_by_gap(
        user_region=data.user_region,
        food_names=data.food_names,
        top_n=data.top_n
    )
    return result.to_dict(orient="records")



# ==== Complication Input ====
class SymptomInput(BaseModel):
    bleeding: str
    pain: str
    vomiting: str
    swelling: int
    headache: int
    dizziness: int
    fatigue: int
    temperature: str
    urine_color: str
    fetal_movement: str

@app.post("/predict-complication")
def predict_complication(symptom: SymptomInput):
    condition = complication_model.predict(symptom.dict())
    return {"predicted_condition": condition}



@app.get("/recipes/search")
def search_recipes(q: str = Query(..., min_length=1)):
    q_lower = q.lower()
    results = [
        {
            "id": r["id"],
            "name": r["name"],
            "category": r["category"],
            "calories": r["calories"],
            "protein": r["protein"],
            "fat": r["fat"],
            "carbs": r["carbs"],
            "iron": r["iron"],
            "calcium": r["calcium"],
            "vitaminA": r["vitaminA"],
            "vitaminC": r["vitaminC"],
            "folate": r["folate"]
        }
        for r in recipes if q_lower in r["name"].lower()
    ]
    return results

# Other endpoints...

app.include_router(articles_router)

app.include_router(meals_router)

app.include_router(recipes_router)

app.include_router(recommendations)

app.include_router(intake_router)

app.include_router(sperm_router)
















































# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# import joblib
# import pandas as pd
# import os

# app = FastAPI()

# # Load model and encoders
# BASE_DIR = os.path.dirname(__file__)
# model = joblib.load(os.path.join(BASE_DIR, "model", "pregnancy_model.joblib"))
# encoders = joblib.load(os.path.join(BASE_DIR, "model", "target_encoder.joblib"))

# # Define symptom input schema
# class SymptomInput(BaseModel):
#     bleeding: str
#     pain: str
#     vomiting: str
#     swelling: int
#     headache: int
#     dizziness: int
#     fatigue: int
#     temperature: str
#     urine_color: str
#     fetal_movement: str

# # Prediction endpoint
# @app.post("/predict")
# def predict(symptom: SymptomInput):
#     input_dict = symptom.dict()
#     df = pd.DataFrame([input_dict])

#     # Encode categorical features
#     for col in encoders:
#         df[col] = encoders[col].transform(df[col])

#     # Predict
#     prediction = model.predict(df)[0]
#     return {"predicted_condition": prediction}










































# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# import joblib
# import pandas as pd
# import os

# app = FastAPI()

# # Load model and encoders
# BASE_DIR = os.path.dirname(__file__)
# model = joblib.load(os.path.join(BASE_DIR, "model", "pregnancy_model.joblib"))
# encoders = joblib.load(os.path.join(BASE_DIR, "model", "target_encoder.joblib"))

# # Define symptom input schema
# class SymptomInput(BaseModel):
#     bleeding: str
#     pain: str
#     vomiting: str
#     swelling: int
#     headache: int
#     dizziness: int
#     fatigue: int
#     temperature: str
#     urine_color: str
#     fetal_movement: str

# # Prediction endpoint
# @app.post("/predict")
# def predict(symptom: SymptomInput):
#     input_dict = symptom.dict()
#     df = pd.DataFrame([input_dict])

#     # Encode categorical features
#     for col in encoders:
#         df[col] = encoders[col].transform(df[col])

#     # Predict
#     prediction = model.predict(df)[0]
#     return {"predicted_condition": prediction}
