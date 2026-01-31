# model.py
import pandas as pd
import numpy as np
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score

# -------------------------------------------------
# 1. Load cleaned dataset
# -------------------------------------------------
# Attempt to load cleaned dataset from several common locations; fall back to raw `data/ev.csv`.
possible_paths = [
    "CLEANED_EV_DATA.csv",
    os.path.join("data", "ev.csv"),
    os.path.join(os.getcwd(), "data", "ev.csv"),
    os.path.expanduser("~/Desktop/CLEANED_EV_DATA.csv"),
    "C:/Users/aravi/OneDrive/Desktop/CLEANED_EV_DATA.csv",
]

df = None
for p in possible_paths:
    try:
        df = pd.read_csv(p)
        print(f"Loaded dataset from: {p}")
        break
    except Exception:
        df = None

if df is None:
    raise FileNotFoundError(
        "Could not find dataset. Checked: " + ", ".join(possible_paths)
    )

# Ensure engineered features exist (some are created by `data.py`). If missing, compute them.
derived_cols = {
    "Battery_Efficiency_km_per_kWh": lambda d: d["Range_km"] / d["Battery_Capacity_kWh"],
    "Charging_Efficiency_km_per_hr": lambda d: d["Range_km"] / d["Charge_Time_hr"],
    "Battery_Capacity_per_Hour": lambda d: d["Battery_Capacity_kWh"] / d["Charge_Time_hr"],
}

for col, func in derived_cols.items():
    if col not in df.columns:
        try:
            df[col] = func(df)
            print(f"Created derived column: {col}")
        except Exception as e:
            print(f"Failed to create {col}: {e}")

# -------------------------------------------------
# 2. Feature selection
# -------------------------------------------------
features = [
    "Year",
    "Battery_Capacity_kWh",
    "Range_km",
    "Charge_Time_hr",
    "Price_USD",
    "Safety_Rating",
    "Warranty_Years",
    "Battery_Efficiency_km_per_kWh",
    "Charging_Efficiency_km_per_hr",
    "Battery_Capacity_per_Hour"
]

target = "Units_Sold_2024"

# -------------------------------------------------
# 3. Encode categorical columns
# -------------------------------------------------
label_encoders = {}

for col in ["Manufacturer", "Battery_Type", "Charging_Type", "Country_of_Manufacture"]:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

features.extend([
    "Manufacturer",
    "Battery_Type",
    "Charging_Type",
    "Country_of_Manufacture"
])

# -------------------------------------------------
# 4. Train-test split
# -------------------------------------------------
# Verify required columns exist before selecting features/target
missing_features = [c for c in features if c not in df.columns]
if missing_features:
    raise KeyError(
        "Missing feature columns: " + ", ".join(missing_features) + ".\n"
        "Run `data.py` to create derived features or provide a cleaned dataset."
    )

if target not in df.columns:
    raise KeyError(f"Target column '{target}' not found in dataset.")

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------------------------
# 5. Train model
# -------------------------------------------------
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=12,
    random_state=42
)

model.fit(X_train, y_train)

# -------------------------------------------------
# 6. Model evaluation
# -------------------------------------------------
y_pred = model.predict(X_test)

print("\n📊 MODEL PERFORMANCE")
print("MAE :", round(mean_absolute_error(y_test, y_pred), 2))
print("R²  :", round(r2_score(y_test, y_pred), 2))

# -------------------------------------------------
# 7. Historical sales (2015–2025)
# -------------------------------------------------
past_sales = (
    df[(df["Year"] >= 2015) & (df["Year"] <= 2025)]
    .groupby("Manufacturer")["Units_Sold_2024"]
    .mean()
)

# -------------------------------------------------
# 8. Predict 2026 sales
# -------------------------------------------------
df_2026 = df.copy()
df_2026["Year"] = 2026

df_2026["Predicted_2026"] = model.predict(df_2026[features])

future_sales = (
    df_2026.groupby("Manufacturer")["Predicted_2026"]
    .mean()
)

# -------------------------------------------------
# 9. Print final output
# -------------------------------------------------
print("\n📈 COMPANY-WISE EV SALES COMPARISON\n")

print(f"{'Company':20} {'Avg(2015-25)':>15} {'2026 Pred':>12} {'Change':>12} {'Change %':>10}")
print("-" * 75)

for m in past_sales.index:
    past = past_sales[m]
    future = future_sales[m]
    change = future - past
    change_pct = (change / past) * 100 if past != 0 else 0

    company_name = label_encoders["Manufacturer"].inverse_transform([m])[0]

    print(
        f"{company_name:20} "
        f"{int(past):15} "
        f"{int(future):12} "
        f"{int(change):12} "
        f"{change_pct:9.2f}%"
    )

print("\n✅ Prediction completed (terminal output only)")
