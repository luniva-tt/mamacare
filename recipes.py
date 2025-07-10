from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter()

RECIPES_PATH = os.path.join(os.path.dirname(__file__), "recipes.json")

with open(RECIPES_PATH, "r", encoding="utf-8") as f:
    recipes = json.load(f)

@router.get("/recipes")
def list_recipes():
    # Return only id and name (and maybe category)
    return [{"id": r["id"], "name": r["name"], "category": r["category"]} for r in recipes]

@router.get("/recipes/{recipe_id}")
def get_recipe(recipe_id: int):
    for recipe in recipes:
        if recipe["id"] == recipe_id:
            return recipe
    raise HTTPException(status_code=404, detail="Recipe not found")
