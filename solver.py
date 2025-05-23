import json
import numpy as np
import cvxpy as cp
import pandas as pd
import helpers

# --- Step 1: Load Data ---
with open("extracted/extracted-heilman-dining-hall-lunch-2025-2025-06-01.json", "r") as f:
    menu = helpers.flatten_sectioned_menu(json.load(f))

# --- Step 2: Define Macro Targets ---
target = {
    "calories": 700,
    "g_protein": 30,
    "g_carbs": 70,
    "g_fat": 20
}

# create a goal vector
g = np.array([target["calories"], target["g_protein"], target["g_carbs"], target["g_fat"]])

# --- Step 3: Realistic Portion Sizes Allowed ---
serving_sizes = [0.5, 1, 1.5, 2, 2.5, 3]  # no zero because we model "off" by turning all binaries off
n_sizes = len(serving_sizes)

# --- Step 4: Extract Items & Build Matrix A ---
food_items = []
macro_rows = { "calories": [], "g_protein": [], "g_carbs": [], "g_fat": [] }

for item in menu:
    try:
        n = item["nutrition"]
        row = [n["calories"], n["g_protein"], n["g_carbs"], n["g_fat"]]
        if all(isinstance(x, (int, float)) for x in row):
            food_items.append(item["name"])
            for key, val in zip(macro_rows.keys(), row):
                macro_rows[key].append(val)
    except:
        continue

n_items = len(food_items)
A = np.array([
    macro_rows["calories"],
    macro_rows["g_protein"],
    macro_rows["g_carbs"],
    macro_rows["g_fat"]
])  # shape: (4, n_items)

# --- Step 5: Decision Variables ---
# b[i][k] = whether food item i is selected at serving size k
b = [
    [cp.Variable(boolean=True) for _ in range(n_sizes)]
    for _ in range(n_items)
]

# --- Step 6: Build x_i = sum(b_ik * size_k) and Total Macros ---
# x_vars is the solution vector containing the serving sizes for each food item in food_items
x_vars = [cp.sum([b[i][k] * serving_sizes[k] for k in range(n_sizes)]) for i in range(n_items)]

# Total macros: A @ x_vars
# mathematical equivalent of total_macros = A * x_vars
total_macros = A @ cp.hstack(x_vars)

# --- Step 7: Define Objective ---
objective = cp.Minimize(cp.sum_squares(total_macros - g))

# --- Step 8: Constraints ---
constraints = []

# At most one serving size per item
for i in range(n_items):
    constraints.append(cp.sum(b[i]) <= 1)

# Optional: Limit total number of food items used
# total_items_used = sum(any b[i][k] is on)
# Approximate by: sum of all b_ik <= 4

constraints.append(cp.sum([b[i][k] for i in range(n_items) for k in range(n_sizes)]) <= 6)

# --- Step 9: Solve ---
problem = cp.Problem(objective, constraints)
problem.solve(solver=cp.ECOS_BB, verbose=False)

# --- Step 10: Extract Results ---
result = []
for i, x in enumerate(x_vars):
    val = x.value
    if val and val > 0.01:
        result.append({
            "name": food_items[i],  # or "id" depending on how we track it
            "servings": round(val, 2)
        })


# --- Display as DataFrame ---
df = pd.DataFrame(result)
print(df)

# Convert x_vars into a flat vector of solved values
x_values = np.array([x.value for x in x_vars])

# Compute total macros actually achieved
actual_macros = A @ x_values  # shape: (4,)

# Define goal vector again for comparison
goal_macros = g  # should be shape: (4,)

# Define labels to print clearly
macro_labels = ["Calories", "Protein (g)", "Carbs (g)", "Fat (g)"]

# Print results
print("\n--- Macro Results ---")
for label, actual, goal in zip(macro_labels, actual_macros, goal_macros):
    diff = actual - goal
    print(f"{label:<15}: {actual:.2f} (goal: {goal:.2f}, diff: {diff:+.2f})")
