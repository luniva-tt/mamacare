# routers/recommendations.py

from fastapi import APIRouter, HTTPException
import pandas as pd
import json
import os

from cosine import recommend_foods  # this should be your own function

router = APIRouter()

@router.get("/foodrecommendation/{user_id}")
def get_recommendations(user_id: str, top_n: int = 5):
    try:
        print("🔍 Request received for:", user_id)

        # ✅ Load data INSIDE the route
        food_df = pd.read_csv("nepalifood.csv")

        with open("user_profiles.json", "r", encoding="utf-8") as f:
            user_profiles = json.load(f)

        with open("threshold.json", "r", encoding="utf-8") as f:
            threshold_data = json.load(f)["nutrient_thresholds"]

        # ✅ Call your recommender function
        top_foods = recommend_foods(user_id, user_profiles, threshold_data, food_df, top_n)

        # ✅ Return simplified output for now
        return top_foods[[
            "food_name", "region", "similarity"
        ]].to_dict(orient="records")

    except ValueError as e:
        print("❌ ValueError:", e)
        raise HTTPException(status_code=404, detail=str(e))

    except Exception as e:
        print("❌ Unknown error:", e)
        raise HTTPException(status_code=500, detail="Internal server error")


















# # routers/recommendations.py
# from fastapi import APIRouter, HTTPException
# import pandas as pd
# import json
# from cosine import recommend_foods  # <-- we now import your function

# router = APIRouter()

# # Load data once
# food_df = pd.read_csv("nepalifood.csv")
# with open("user_profiles.json") as f:
#     user_profiles = json.load(f)
# with open("threshold.json") as f:
#     threshold_data = json.load(f)["nutrient_thresholds"]

# @router.get("/foodrecommendation/{user_id}")
# def get_recommendations(user_id: str, top_n: int = 5):
#     user_id = "user_001"
#     try:
#         top_foods = recommend_foods(user_id, user_profiles, threshold_data, food_df, top_n)
#         return top_foods[[
#             "food_name", "region", "similarity",
#             "calories", "protein", "fat", "carbs", "iron",
#             "calcium", "vitaminA", "vitaminC", "folate"
#         ]].to_dict(orient="records")
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))
