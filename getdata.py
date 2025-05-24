import requests
from datetime import datetime
import os
import json

# Function to fetch menu data for a specific dining hall
dining_halls = ['tylers', 'eight-fifteen', 'heilman-dining-hall', 'lous', 'passport']
the_celler = 'the-cellar'  # Exception

# Breakfast Lunch Dinner
meal_types = ['breakfast', 'lunch', 'dinner']

def fetch_menu(dining_hall, meal_type, date=datetime.now()):
    district = 'richmond'
    year = date.year
    month = date.strftime('%m')
    day = date.strftime('%d')

    if dining_hall != the_celler:
        url = f'https://{district}.api.nutrislice.com/menu/api/weeks/school/{dining_hall}/menu-type/{meal_type}/{year}/{month}/{day}/?format=json'
    else:
        url = f'https://{district}.api.nutrislice.com/menu/api/weeks/school/{the_celler}/menu-type/dinner/{year}/{month}/{day}/?format=json'

    response = requests.get(url)
    if response.status_code == 200:
        return response.json(), year, month, day
    else:
        return None, year, month, day

# Fetching menu for a location
dining_location = "heilman-dining-hall"
meal_type = "lunch"
menu_data, year, month, day = fetch_menu(dining_location, meal_type, datetime(year=2025, month=6, day=3))

# Naming the file
first_date = menu_data["days"][0]["date"]
filename = f"{dining_location}-{meal_type}-{first_date}.json"

# Ensure the 'raw/' directory exists
os.makedirs("raw", exist_ok=True)

if menu_data:
    print("Menu Data Fetched Successfully")
    with open("raw/" + filename, 'w') as file:
        json.dump(menu_data, file, indent=2)
else:
    print("Failed to Fetch Menu Data")