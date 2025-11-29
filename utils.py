import os
from datetime import datetime
import pandas as pd

DATA_DIR = "data"


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def calculate_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
    gender = gender.lower()
    if gender == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def activity_multiplier(level: str) -> float:
    mapping = {
        "Sedentary (little or no exercise)": 1.2,
        "Light (1-3 days/week)": 1.375,
        "Moderate (3-5 days/week)": 1.55,
        "Active (6-7 days/week)": 1.725,
        "Very active (hard exercise & physical job)": 1.9,
    }
    return mapping.get(level, 1.2)


def calorie_target(tdee: float, goal: str) -> float:
    if goal == "Lose weight":
        return tdee - 500
    elif goal == "Gain weight":
        return tdee + 300
    return tdee


def macro_targets(weight_kg: float, calories: float) -> dict:
    protein_g = 1.8 * weight_kg
    protein_cal = protein_g * 4

    fat_cal = 0.25 * calories
    fat_g = fat_cal / 9

    remaining_cal = calories - protein_cal - fat_cal
    carbs_g = remaining_cal / 4 if remaining_cal > 0 else 0

    return {
        "protein_g": round(protein_g, 1),
        "fat_g": round(fat_g, 1),
        "carbs_g": round(carbs_g, 1),
    }


def bmi_and_category(weight_kg: float, height_cm: float):
    height_m = height_cm / 100
    if height_m <= 0:
        return 0.0, "Invalid height"
    bmi = weight_kg / (height_m ** 2)
    if bmi < 18.5:
        cat = "Underweight"
    elif bmi < 25:
        cat = "Normal"
    elif bmi < 30:
        cat = "Overweight"
    else:
        cat = "Obese"
    return round(bmi, 1), cat


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def load_csv(path: str, default_columns=None) -> pd.DataFrame:
    ensure_data_dir()
    if not os.path.exists(path):
        if default_columns:
            return pd.DataFrame(columns=default_columns)
        return pd.DataFrame()
    return pd.read_csv(path)


def save_csv(df: pd.DataFrame, path: str):
    ensure_data_dir()
    df.to_csv(path, index=False)

