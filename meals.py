from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json
import os
from datetime import datetime

router = APIRouter()

MEALS_PATH = os.path.join(os.path.dirname(__file__), "logged_meals.json")
FOOD_CSV_PATH = os.path.join(os.path.dirname(__file__), "nepalifood.csv")

class MealLog(BaseModel):
    user_id: str
    food_id: int
    date: Optional[str] = None  # Defaults to today if not provided

@router.post("/logmeal")
def log_meal(meal: MealLog):
    # Load food list to validate food_id
    import pandas as pd
    food_df = pd.read_csv(FOOD_CSV_PATH)
    food_row = food_df[food_df["food_id"] == meal.food_id]
    if food_row.empty:
        raise HTTPException(status_code=404, detail="Food ID not found")

    food_name = food_row.iloc[0]["food_name"]

    # Set date to today if not provided
    if not meal.date:
        meal.date = datetime.today().strftime("%Y-%m-%d")

    # Load current logs
    if os.path.exists(MEALS_PATH):
        with open(MEALS_PATH, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []

    # Append new log
    logs.append({
        "user_id": meal.user_id,
        "food_id": meal.food_id,
        "food_name": food_name,
        "date": meal.date,
    })

    # Save updated log
    with open(MEALS_PATH, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

    return {"message": "Meal logged successfully"}

@router.get("/logmeal/{user_id}")
def get_logged_meals(user_id: str):
    if not os.path.exists(MEALS_PATH):
        return []

    with open(MEALS_PATH, "r", encoding="utf-8") as f:
        logs = json.load(f)

    return [log for log in logs if log["user_id"] == user_id]
