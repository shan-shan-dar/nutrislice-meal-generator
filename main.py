import json

import os
import solver
import helpers

helpers.flatten_all_extracted_menus()

filename = "extracted-heilman-dining-hall-lunch-2025-06-02.json"
with open("extracted/" + filename, "r") as f:
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

with open("solved/" + filename.replace("extracted-", "solved-"), "w") as f:
    json.dump(meal_json, f, indent=2)