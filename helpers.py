def flatten_sectioned_menu(sectioned_menu):
    flat_menu = []

    for section_name, items in sectioned_menu.items():
        for item in items:
            item_with_section = item.copy()
            item_with_section["section"] = section_name
            flat_menu.append(item_with_section)

    return flat_menu