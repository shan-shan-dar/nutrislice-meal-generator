import os
import json

def flatten_sectioned_menu(sectioned_menu):
    flat_menu = []

    for section_name, items in sectioned_menu.items():
        for item in items:
            item_with_section = item.copy()
            item_with_section["section"] = section_name
            flat_menu.append(item_with_section)

    return flat_menu

def flatten_all_extracted_menus(extracted_dir="extracted", output_dir="flattened"):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(extracted_dir):
        if not filename.startswith("extracted-") or not filename.endswith(".json"):
            continue

        try:
            input_path = os.path.join(extracted_dir, filename)
            with open(input_path, "r") as f:
                sectioned_menu = json.load(f)

            flat_menu = flatten_sectioned_menu(sectioned_menu)

            output_filename = filename.replace("extracted-", "flattened-")
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, "w") as out_file:
                json.dump(flat_menu, out_file, indent=2)

            print(f"Flattened: {output_filename}")

        except Exception as e:
            print(f"Failed to process {filename}: {e}")