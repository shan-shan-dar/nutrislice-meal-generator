import json
import os
import re

def clean_ingredients(text):
    if not isinstance(text, str):
        return ""
    # Remove anything inside () or []
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    # Replace all punctuation with space
    text = re.sub(r'[^\w\s]', ' ', text)
    # Normalize all whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip().lower()


def extract_day_menu(day_obj):
    sections = {}
    current_section = "Uncategorized"

    for idx, item in enumerate(day_obj.get("menu_items", [])):
        # Update section if this item is a section header
        if item.get("is_section_title"):
            current_section = item.get("text", "Unnamed Section").strip()
            sections.setdefault(current_section, [])
            continue

        food = item.get("food")
        if not food:
            continue

        
        name = food.get("name", "")

        icons = [
            icon.get("synced_name")
            for icon in food.get("icons", {}).get("food_icons", [])
            if "synced_name" in icon
        ]
        
        extracted_entry = {
            "name": name,
            "ingredients": clean_ingredients(food.get("ingredients", "")),
            "nutrition": food.get("rounded_nutrition_info", {}),
            "serving_size": food.get("serving_size_info", {}),
            "icons": icons,
            "icons_string": ", ".join(icons)
        }

        # Add to current section
        sections.setdefault(current_section, []).append(extracted_entry)

    # Assign globally unique IDs across all sections
    global_id = 0
    for section_items in sections.values():
        for item in section_items:
            item["id"] = global_id
            global_id += 1

    return sections


def extract_all_days_from_raw_files(raw_dir="raw", output_dir="extracted"):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(raw_dir):
        if not filename.endswith(".json"):
            continue

        try:
            # Split: e.g., heilman-dining-hall-lunch-2025-06-01.json
            name_parts = filename.replace(".json", "").split("-")
            dining_place = "-".join(name_parts[:-4])  # drop both year and day from filename parts
            # handles hyphenated place names
            meal_type = name_parts[-4]

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