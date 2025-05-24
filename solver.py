import json
import numpy as np
import cvxpy as cp
import pandas as pd
import helpers

def solve_meal_plan(menu, target):
    # --- Define Target Vector ---
    g = np.array([
        target["calories"],
        target["g_protein"],
        target["g_carbs"],
        target["g_fat"]
    ])

    # --- Define Serving Sizes ---
    serving_sizes = np.arange(0.5,5,0.5)#[0.5, 1, 1.5, 2, 2.5, 3]
    n_sizes = len(serving_sizes)

    # --- Construct Items & Macro Matrix ---
    food_items = []
    macro_rows = { "calories": [], "g_protein": [], "g_carbs": [], "g_fat": [] }
    item_id_map = []

    for item in menu:
        try:
            n = item["nutrition"]
            row = [n["calories"], n["g_protein"], n["g_carbs"], n["g_fat"]]
            if all(isinstance(x, (int, float)) for x in row):
                food_items.append(item)
                item_id_map.append(item["id"])
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
    ]) 

    # --- Decision Variables ---
    b = [
        [cp.Variable(boolean=True) for _ in range(n_sizes)]
        for _ in range(n_items)
    ]

    # final solution vector
    x_vars = [cp.sum([b[i][k] * serving_sizes[k] for k in range(n_sizes)]) for i in range(n_items)]
    total_macros = A @ cp.hstack(x_vars)

    # --- Solver Objective ---
    objective = cp.Minimize(cp.sum_squares(total_macros - g))

    # --- Constraints ---
    constraints = []

    # 1. Each item can only be selected once or 0 times
    for i in range(n_items):
        constraints.append(cp.sum(b[i]) <= 1)  

    # 2. There can be at most max_item items in the meal (for now. this will probably be a soft constraint eventually)
    max_items = 15
    constraints.append(cp.sum([b[i][k] for i in range(n_items) for k in range(n_sizes)]) <= max_items)  

    # --- Solve ---
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.ECOS_BB, verbose=False)

    # --- Build Result JSON ---
    result = []
    x_values = np.array([x.value for x in x_vars])
    for i, val in enumerate(x_values):
        if val and val > 0.01:
            entry = dict(food_items[i])  # deep copy from input
            entry["servings"] = round(val, 2)
            result.append(entry)

    # --- Print Summary and Return Result JSON ---
    actual_macros = A @ x_values
    macro_labels = ["Calories", "Protein (g)", "Carbs (g)", "Fat (g)"]

    print("\n--- Solved Meal ---")
    df = pd.DataFrame([{"name": i["name"], "servings": i["servings"]} for i in result])
    print(df)

    print("\n--- Macro Results ---")
    for label, actual, goal_val in zip(macro_labels, actual_macros, g):
        diff = actual - goal_val
        print(f"{label:<15}: {actual:.2f} (error: {diff:+.2f})")

    return {
        "goal": target,
        "totals": {
            "calories": round(actual_macros[0], 2),
            "g_protein": round(actual_macros[1], 2),
            "g_carbs": round(actual_macros[2], 2),
            "g_fat": round(actual_macros[3], 2)
        },
        "meal": result
    }
