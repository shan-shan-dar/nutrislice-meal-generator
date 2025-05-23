import json
import os

def extract_day_menu(day_obj):
    extracted_foods = []

    for idx, item in enumerate(day_obj.get("menu_items", [])):
        food = item.get("food")
        if not food:
            continue

        extracted_entry = {
            "id": idx - 1,  # Unique ID based on order in JSON
            "name": food.get("name", ""),
            "ingredients": food.get("ingredients", ""),
            "nutrition": food.get("rounded_nutrition_info", {}),
            "serving_size": food.get("serving_size_info", {}),
            "icons": [
                icon.get("synced_name")
                for icon in food.get("icons", {}).get("food_icons", [])
                if "synced_name" in icon
            ]
        }

        extracted_foods.append(extracted_entry)

    return extracted_foods


def extract_all_days_from_raw_files(raw_dir="raw", output_dir="extracted"):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(raw_dir):
        if not filename.endswith(".json"):
            continue

        try:
            # Split: e.g., heilman-dining-hall-lunch-2025-06-01.json
            name_parts = filename.replace(".json", "").split("-")
            dining_place = "-".join(name_parts[:-3])  # handles hyphenated place names
            meal_type = name_parts[-3]

            with open(os.path.join(raw_dir, filename), "r") as f:
                menu_data = json.load(f)

            for day in menu_data.get("days", []):
                date = day.get("date")
                if not date:
                    continue

                extracted = extract_day_menu(day)

                out_filename = f"extracted-{dining_place}-{meal_type}-{date}.json"
                out_path = os.path.join(output_dir, out_filename)

                with open(out_path, "w") as out_file:
                    json.dump(extracted, out_file, indent=2)

                print(f"Extracted: {out_filename}")

        except Exception as e:
            print(f"Failed to extract from {filename}: {e}")

extract_all_days_from_raw_files()