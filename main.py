import json

import os
import solver
import helpers

with open("extracted/extracted-heilman-dining-hall-lunch-2025-2025-06-02.json", "r") as f:
    raw_menu = json.load(f)
menu = helpers.flatten_sectioned_menu(raw_menu)

target = {
    "calories": 2100,
    "g_protein": 180,
    "g_carbs": 212,
    "g_fat": 58
}

meal_json = solver.solve_meal_plan(menu, target)

# Ensure the 'raw/' directory exists
os.makedirs("solved", exist_ok=True)

with open("solved/solved-heilman-dining-hall-lunch-2025-2025-06-02.json", "w") as f:
    json.dump(meal_json, f, indent=2)