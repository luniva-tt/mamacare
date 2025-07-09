import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

class NutrientGapRecommender:
    def __init__(self, dataset_path):
        self.df = pd.read_csv(dataset_path)
        self.features = ['calories', 'protein', 'fat', 'carbs', 'iron',
                         'calcium', 'vitaminA', 'vitaminC', 'folate']
        self.scaler = MinMaxScaler()
        self.thresholds = self.set_thresholds()

    def set_thresholds(self):
        return {
            'calories': 2500,
            'protein': 71,
            'fat': 70,
            'carbs': 300,
            'iron': 27,
            'calcium': 1000,
            'vitaminA': 770,
            'vitaminC': 85,
            'folate': 600
        }

    def filter_by_region(self, user_region):
        return self.df[(self.df['region'] == user_region) | (self.df['region'] == 'All')].copy()

    def calculate_intake(self, food_names):
        selected = self.df[self.df['food_name'].isin(food_names)]
        intake = selected[self.features].sum().to_dict()
        return intake

    def calculate_nutrient_gap(self, intake):
        gap = {}
        for key in self.features:
            required = self.thresholds.get(key, 0)
            consumed = intake.get(key, 0)
            gap[key] = max(required - consumed, 0)
        return gap

    def recommend_by_gap(self, user_region, food_names, top_n=5):
        intake = self.calculate_intake(food_names)
        gap = self.calculate_nutrient_gap(intake)

        filtered_df = self.filter_by_region(user_region)
        if filtered_df.empty:
            return pd.DataFrame(columns=['food_name', 'region', 'similarity'])

        nutrition_data = filtered_df[self.features]
        scaled_data = self.scaler.fit_transform(nutrition_data)

        gap_vector = self.scaler.transform([[gap.get(f, 0.0) for f in self.features]])
        similarities = cosine_similarity(gap_vector, scaled_data).flatten()
        filtered_df['similarity'] = similarities

        top_foods = filtered_df.sort_values(by='similarity', ascending=False)
        return top_foods[['food_name', 'region', 'iron', 'folate', 'protein', 'calcium', 'similarity']].head(top_n)
