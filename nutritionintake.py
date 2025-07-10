from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import json
import os

router = APIRouter()

MEALS_PATH = os.path.join(os.path.dirname(__file__), "logged_meals.json")
FOOD_PATH = os.path.join(os.path.dirname(__file__), "nepalifood.csv")
USERS_PATH = os.path.join(os.path.dirname(__file__), "user_profiles.json")
THRESHOLD_PATH = os.path.join(os.path.dirname(__file__), "threshold.json")

# Nutrients tracked in your food CSV and user intake
nutrients = [
    "protein", "fat", "carbs", "iron", "calcium",
    "vitaminA", "vitaminC", "folate", "iodine"
]

# Map simplified names to those used in threshold.json
key_mapping = {
    "protein": "protein_g",
    "fat": "fat_g",
    "carbs": "carbs_g",
    "iron": "iron_mg",
    "calcium": "calcium_mg",
    "vitaminA": "vitamin_a_mcg",
    "vitaminC": "vitamin_c_mg",
    "folate": "folic_acid_mcg",
    "iodine": "iodine_mcg"
}


@router.get("/nutrientsummary/{user_id}")
def nutrient_summary(user_id: str, date: str = Query(...)):
    # Load all data
    try:
        food_df = pd.read_csv(FOOD_PATH)
        with open(MEALS_PATH, "r", encoding="utf-8") as f:
            meals = json.load(f)
        with open(USERS_PATH, "r", encoding="utf-8") as f:
            users = json.load(f)
        with open(THRESHOLD_PATH, "r", encoding="utf-8") as f:
            thresholds = json.load(f)["nutrient_thresholds"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading data: {e}")

    # Get user
    user = next((u for u in users if u["user_id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get meals logged on that date
    meals_today = [m for m in meals if m["user_id"] == user_id and m["date"] == date]
    if not meals_today:
        return {"message": "No meals logged for this date", "intake": {}, "percentages": {}}

    # Sum up nutrient intake
    total_intake = {k: 0.0 for k in nutrients}
    for meal in meals_today:
        food_row = food_df[food_df["food_id"] == meal["food_id"]]
        if food_row.empty:
            continue
        row = food_row.iloc[0]
        for nutrient in nutrients:
            total_intake[nutrient] += row[nutrient]

    # Build threshold for user's stage and preconditions
    base_thresh = thresholds.get(user["stage"].lower(), {})
    combined_threshold = {}

    # Start with stage thresholds
    for k, v in key_mapping.items():
        combined_threshold[k] = base_thresh.get(v, 0)

    # Merge with conditions (take max of each)
    for condition, present in user["preconditions"].items():
        if present:
            cond_thresh = thresholds.get(condition.lower(), {})
            for k, v in key_mapping.items():
                combined_threshold[k] = max(
                    combined_threshold.get(k, 0),
                    cond_thresh.get(v, 0)
                )

    # Calculate % of required nutrients consumed
    percentage_intake = {}
    for n in nutrients:
        required = combined_threshold.get(n, 0)
        consumed = total_intake.get(n, 0)
        if required == 0:
            percentage = 0
        else:
            percentage = round((consumed / required) * 100, 2)
        percentage_intake[n] = min(percentage, 999.0)

    return {
        "date": date,
        "user_id": user_id,
        "intake": total_intake,
        "threshold": {n: combined_threshold.get(n, 0) for n in nutrients},
        "percentages": percentage_intake
    }































# from fastapi import APIRouter, HTTPException, Query
# import pandas as pd
# import json
# import os

# router = APIRouter()

# MEALS_PATH = os.path.join(os.path.dirname(__file__), "logged_meals.json")
# FOOD_PATH = os.path.join(os.path.dirname(__file__), "nepalifood.csv")
# USERS_PATH = os.path.join(os.path.dirname(__file__), "user_profiles.json")
# THRESHOLD_PATH = os.path.join(os.path.dirname(__file__), "threshold.json")

# nutrients = [
#     "protein", "fat", "carbs", "iron", "calcium",
#     "vitaminA", "vitaminC", "folate", "iodine"
# ]

# key_mapping = {
#     "protein": "protein_g",
#     "fat": "fat_g",
#     "carbs": "carbs_g",
#     "iron": "iron_mg",
#     "calcium": "calcium_mg",
#     "vitaminA": "vitamin_a_mcg",
#     "vitaminC": "vitamin_c_mg",
#     "folate": "folic_acid_mcg",
#     "iodine": "iodine_mcg"
# }


# @router.get("/nutrientsummary/{user_id}")
# def nutrient_summary(user_id: str, date: str = Query(...)):
#     # Load all data
#     try:
#         food_df = pd.read_csv(FOOD_PATH)
#         with open(MEALS_PATH, "r", encoding="utf-8") as f:
#             meals = json.load(f)
#         with open(USERS_PATH, "r", encoding="utf-8") as f:
#             users = json.load(f)
#         with open(THRESHOLD_PATH, "r", encoding="utf-8") as f:
#             thresholds = json.load(f)["nutrient_thresholds"]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error loading data: {e}")

#     # Get user
#     user = next((u for u in users if u["user_id"] == user_id), None)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Get meals logged on that date
#     meals_today = [m for m in meals if m["user_id"] == user_id and m["date"] == date]
#     if not meals_today:
#         return {"message": "No meals logged for this date", "intake": {}, "percentages": {}}

#     # Sum up nutrient intake
#     total_intake = {k: 0.0 for k in nutrients}
#     for meal in meals_today:
#         food_row = food_df[food_df["food_id"] == meal["food_id"]]
#         if food_row.empty:
#             continue
#         row = food_row.iloc[0]
#         for nutrient in nutrients:
#             total_intake[nutrient] += row[nutrient]

#     # Get threshold (stage + conditions)
#     combined_threshold = thresholds.get(user["stage"], {})
#     for condition, present in user["preconditions"].items():
#         if present:
#             cond_thresh = thresholds.get(condition.lower(), {})
#             for k, v in cond_thresh.items():
#                 combined_threshold[k] = max(combined_threshold.get(k, 0), v)

#     # Calculate percentage intake
#     percentage_intake = {}
#     for n in nutrients:
#         required = combined_threshold.get(n, 1e-10)  # avoid div by zero
#         consumed = total_intake.get(n, 0)
#         percentage = round((consumed / required) * 100, 2)
#         percentage_intake[n] = min(percentage, 999.0)  # cap at 999%

#     return {
#         "date": date,
#         "user_id": user_id,
#         "intake": total_intake,
#         "threshold": {n: combined_threshold.get(n, 0) for n in nutrients},
#         "percentages": percentage_intake
#     }
