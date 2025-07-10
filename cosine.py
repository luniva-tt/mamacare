# # # cosine.py
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np
# import pandas as pd


# # models/cosine.py
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd

def recommend_foods(user_id, user_profiles, threshold_data, food_df, top_n=5):
    nutrient_keys = {
        "protein": "protein_g",
        "fat": "fat_g",
        "carbs": "carbs_g",
        "iron": "iron_mg",
        "calcium": "calcium_mg",
        "vitaminA": "vitamin_a_mcg",
        "vitaminC": "vitamin_c_mg",
        "folate": "folic_acid_mcg"
    }

    # ✅ Get user
    user = next((u for u in user_profiles if u["user_id"] == user_id), None)
    if not user:
        raise ValueError(f"User ID {user_id} not found.")
    
    # ✅ Filter by region
    user_region = user["region"].lower()
    region_filtered_df = food_df[
        (food_df["region"].str.lower() == user_region) | 
        (food_df["region"].str.lower() == "all")
    ].copy().reset_index(drop=True)

    if region_filtered_df.empty:
        raise ValueError(f"No food items found for region: {user_region}")

    # ✅ Merge stage + precondition thresholds
    combined_threshold = threshold_data.get(user["stage"], {})
    for condition, present in user["preconditions"].items():
        if present:
            condition_threshold = threshold_data.get(condition.lower(), {})
            for k, v in condition_threshold.items():
                combined_threshold[k] = max(combined_threshold.get(k, 0), v)

    # ✅ Build user vector
    user_nutrient_vector = np.array([
        combined_threshold.get(thresh_key, 0) 
        for _, thresh_key in nutrient_keys.items()
    ])
    user_norm = np.linalg.norm(user_nutrient_vector)
    if user_norm == 0:
        user_norm = 1e-10  # avoid divide-by-zero
    user_vec_norm = user_nutrient_vector / user_norm

    # ✅ Build food vectors
    food_vectors = region_filtered_df[list(nutrient_keys.keys())].fillna(0).values
    norms = np.linalg.norm(food_vectors, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    food_vectors_norm = food_vectors / norms

    # ✅ Compute cosine similarity
    similarities = cosine_similarity([user_vec_norm], food_vectors_norm)[0]
    region_filtered_df["similarity"] = similarities

    # ✅ Return top N foods
    return region_filtered_df.sort_values(by="similarity", ascending=False).head(top_n)


# def recommend_foods(user_id, user_profiles, threshold_data, food_df, top_n=5):
#     print("📦 Running recommend_foods...")

#     user = next((u for u in user_profiles if u["user_id"] == user_id), None)
#     if not user:
#         raise ValueError(f"User {user_id} not found.")

#     # Dummy sort for now
#     return food_df.head(top_n)

# # def recommend_foods(user_id, user_profiles, threshold_data, food_df, top_n=5):
# #     nutrient_keys = {
# #         "protein": "protein",
# #         "fat": "fat",
# #         "carbs": "carbs",
# #         "iron": "iron",
# #         "calcium": "calcium",
# #         "vitaminA": "vitaminA",
# #         "vitaminC": "vitaminC",
# #         "folate": "folate"
# #     }

# #     # Get the user
# #     user = next((u for u in user_profiles if u["user_id"] == user_id), None)
# #     if not user:
# #         raise ValueError(f"User ID {user_id} not found.")
    
# #     user_region = user["region"].lower()

# #     region_filtered_df = food_df[
# #         (food_df["region"].str.lower() == user_region) | 
# #         (food_df["region"].str.lower() == "all")
# #     ].reset_index(drop=True)

# #     if region_filtered_df.empty:
# #         raise ValueError(f"No food items found for region: {user_region}")

# #     # Combine thresholds from stage and preconditions
# #     combined_threshold = threshold_data.get(user["stage"], {})
# #     for condition, present in user["preconditions"].items():
# #         if present:
# #             condition_threshold = threshold_data.get(condition.lower(), {})
# #             for k, v in condition_threshold.items():
# #                 combined_threshold[k] = max(combined_threshold.get(k, 0), v)

# #     user_nutrient_vector = np.array([
# #         combined_threshold.get(nutrient_keys[n], 0)
# #         for n in nutrient_keys
# #     ])
# #     # user_vec_norm = user_nutrient_vector / np.linalg.norm(user_nutrient_vector)
# #     user_norm = np.linalg.norm(user_nutrient_vector)
# #     if user_norm == 0:
# #         user_norm = 1e-10
# #     user_vec_norm = user_nutrient_vector / user_norm

# #     food_vectors = region_filtered_df[list(nutrient_keys.keys())].fillna(0).values
# #     # food_vectors_norm = food_vectors / np.linalg.norm(food_vectors, axis=1, keepdims=True)
    
# #     norms = np.linalg.norm(food_vectors, axis=1, keepdims=True)
# #     norms[norms == 0] = 1e-10  # Prevent division by 0
# #     food_vectors_norm = food_vectors / norms

# #     similarities = cosine_similarity([user_vec_norm], food_vectors_norm)[0]
# #     region_filtered_df['similarity'] = similarities

# #     return region_filtered_df.sort_values(by='similarity', ascending=False).head(top_n)
