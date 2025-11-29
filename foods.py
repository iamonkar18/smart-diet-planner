import random
import pandas as pd

# Big-ish food database (veg + non-veg, Indian-focused)
FOODS = [
    # Veg breakfast
    {"name": "Poha", "serving": "1 plate", "veg": True, "meal_types": ["breakfast"], "cal": 180, "protein": 3, "carbs": 32, "fat": 4},
    {"name": "Upma", "serving": "1 plate", "veg": True, "meal_types": ["breakfast"], "cal": 200, "protein": 4, "carbs": 35, "fat": 5},
    {"name": "Oats Porridge", "serving": "1 bowl", "veg": True, "meal_types": ["breakfast"], "cal": 150, "protein": 5, "carbs": 25, "fat": 3},
    {"name": "Idli Sambar", "serving": "2 idli + sambar", "veg": True, "meal_types": ["breakfast"], "cal": 220, "protein": 7, "carbs": 40, "fat": 4},
    {"name": "Dosa (plain)", "serving": "1 dosa", "veg": True, "meal_types": ["breakfast"], "cal": 180, "protein": 4, "carbs": 30, "fat": 5},

    # Veg staples
    {"name": "Roti (wheat)", "serving": "1 medium (40g)", "veg": True, "meal_types": ["lunch","dinner"], "cal": 120, "protein": 3, "carbs": 18, "fat": 3},
    {"name": "Boiled Rice", "serving": "1 bowl (100g)", "veg": True, "meal_types": ["lunch","dinner"], "cal": 130, "protein": 2.5, "carbs": 28, "fat": 0.3},
    {"name": "Brown Rice", "serving": "1 bowl (100g)", "veg": True, "meal_types": ["lunch","dinner"], "cal": 120, "protein": 2.6, "carbs": 25, "fat": 1},
    {"name": "Dal Tadka", "serving": "1 bowl", "veg": True, "meal_types": ["lunch","dinner"], "cal": 150, "protein": 9, "carbs": 18, "fat": 5},
    {"name": "Rajma Curry", "serving": "1 bowl", "veg": True, "meal_types": ["lunch","dinner"], "cal": 180, "protein": 9, "carbs": 30, "fat": 4},
    {"name": "Chole (chickpea curry)", "serving": "1 bowl", "veg": True, "meal_types": ["lunch","dinner"], "cal": 190, "protein": 10, "carbs": 30, "fat": 5},
    {"name": "Paneer Bhurji", "serving": "50g", "veg": True, "meal_types": ["lunch","dinner"], "cal": 150, "protein": 9, "carbs": 4, "fat": 11},
    {"name": "Mixed Veg Sabzi", "serving": "1 bowl", "veg": True, "meal_types": ["lunch","dinner"], "cal": 100, "protein": 3, "carbs": 12, "fat": 5},
    {"name": "Salad", "serving": "1 plate", "veg": True, "meal_types": ["lunch","dinner"], "cal": 40, "protein": 2, "carbs": 8, "fat": 1},
    {"name": "Curd (Dahi)", "serving": "1 bowl", "veg": True, "meal_types": ["lunch","dinner","snack"], "cal": 70, "protein": 3.5, "carbs": 5, "fat": 3},

    # Snacks / fruits / nuts
    {"name": "Banana", "serving": "1 piece", "veg": True, "meal_types": ["breakfast","snack"], "cal": 90, "protein": 1, "carbs": 23, "fat": 0.3},
    {"name": "Apple", "serving": "1 piece", "veg": True, "meal_types": ["breakfast","snack"], "cal": 80, "protein": 0.3, "carbs": 21, "fat": 0.2},
    {"name": "Orange", "serving": "1 piece", "veg": True, "meal_types": ["snack"], "cal": 60, "protein": 1, "carbs": 15, "fat": 0.2},
    {"name": "Sprouts Bowl", "serving": "1 bowl", "veg": True, "meal_types": ["breakfast","snack"], "cal": 120, "protein": 8, "carbs": 16, "fat": 1},
    {"name": "Mixed Nuts", "serving": "10-12 pcs", "veg": True, "meal_types": ["snack"], "cal": 100, "protein": 3, "carbs": 4, "fat": 9},
    {"name": "Roasted Chana", "serving": "1 small bowl", "veg": True, "meal_types": ["snack"], "cal": 120, "protein": 6, "carbs": 18, "fat": 2},

    # Non-veg
    {"name": "Boiled Egg", "serving": "1 egg", "veg": False, "meal_types": ["breakfast","snack","dinner"], "cal": 70, "protein": 6, "carbs": 1, "fat": 5},
    {"name": "Egg Bhurji", "serving": "2 eggs", "veg": False, "meal_types": ["breakfast","dinner"], "cal": 200, "protein": 12, "carbs": 4, "fat": 15},
    {"name": "Chicken Breast (cooked)", "serving": "100g", "veg": False, "meal_types": ["lunch","dinner"], "cal": 165, "protein": 31, "carbs": 0, "fat": 4},
    {"name": "Fish Curry", "serving": "1 piece", "veg": False, "meal_types": ["lunch","dinner"], "cal": 200, "protein": 20, "carbs": 8, "fat": 10},
]


def get_foods_for_meal(meal_type: str, veg_only: bool):
    return [
        f for f in FOODS
        if meal_type in f["meal_types"] and (f["veg"] or not veg_only)
    ]


def generate_meal(meal_type: str, meal_calories: float, veg_only: bool, seed: int = None):
    foods = get_foods_for_meal(meal_type, veg_only)
    if not foods:
        return []

    rng = random.Random(seed)
    rng.shuffle(foods)

    items = []
    remaining = meal_calories

    for food in foods[:5]:
        if remaining <= 0:
            break

        max_serv = remaining / food["cal"]
        if max_serv < 0.4:
            continue

        servings = round(min(2.0, max_serv), 1)
        cals = servings * food["cal"]

        items.append({
            "meal_type": meal_type.title(),
            "food": food["name"],
            "serving": food["serving"],
            "servings": servings,
            "calories": round(cals, 0),
            "protein_g": round(servings * food["protein"], 1),
            "carbs_g": round(servings * food["carbs"], 1),
            "fat_g": round(servings * food["fat"], 1),
        })

        remaining -= cals

    return items


def build_full_day_plan(total_calories: float, veg_only: bool, seeds: dict):
    ratios = {
        "breakfast": 0.25,
        "lunch": 0.30,
        "snack": 0.15,
        "dinner": 0.30,
    }

    all_items = []
    for meal, ratio in ratios.items():
        meal_cals = total_calories * ratio
        seed = seeds.get(meal)
        items = generate_meal(meal, meal_cals, veg_only, seed=seed)
        all_items.extend(items)

    df = pd.DataFrame(all_items)
    if df.empty:
        return pd.DataFrame(columns=["meal_type","food","serving","servings","calories","protein_g","carbs_g","fat_g"])
    return df

