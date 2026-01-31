from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# Load dataset using same fallback paths as model_building
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
    raise FileNotFoundError("Could not find dataset. Checked: " + ", ".join(possible_paths))

# Create derived columns if missing
derived_cols = {
    "Battery_Efficiency_km_per_kWh": lambda d: d["Range_km"] / d["Battery_Capacity_kWh"],
    "Charging_Efficiency_km_per_hr": lambda d: d["Range_km"] / d["Charge_Time_hr"],
    "Battery_Capacity_per_Hour": lambda d: d["Battery_Capacity_kWh"] / d["Charge_Time_hr"],
}
for col, func in derived_cols.items():
    if col not in df.columns:
        try:
            df[col] = func(df)
        except Exception:
            df[col] = np.nan

# Fill simple missing numeric values with median to allow training
numeric_cols = [
    'Year','Battery_Capacity_kWh','Range_km','Charge_Time_hr','Price_USD',
    'Safety_Rating','Warranty_Years','Units_Sold_2024'
]
for c in numeric_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')
        df[c] = df[c].fillna(df[c].median())

# Encode categorical columns but keep original Manufacturer for display
cat_cols = ["Manufacturer", "Battery_Type", "Charging_Type", "Country_of_Manufacture"]
label_encoders = {}
for col in cat_cols:
    if col in df.columns:
        le = LabelEncoder()
        df[col + "_enc"] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le

# Features for model
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
    "Battery_Capacity_per_Hour",
]

# Append encoded categorical features if available
for col in cat_cols:
    enc = col + "_enc"
    if enc in df.columns:
        features.append(enc)

# Ensure target exists
if "Units_Sold_2024" not in df.columns:
    raise KeyError("Target column 'Units_Sold_2024' not found in dataset.")

# Prepare X and y
X = df[features]
y = df["Units_Sold_2024"]

# Train model (fast) - regress on available data
model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
model.fit(X, y)

# Compute historical average (2015-2025)
past_sales = df[(df['Year'] >= 2015) & (df['Year'] <= 2025)].groupby('Manufacturer')['Units_Sold_2024'].mean()

# Predict 2026
df_2026 = df.copy()
df_2026['Year'] = 2026
# prepare features for df_2026 (columns must match)
X_2026 = df_2026[features]
df_2026['Predicted_2026'] = model.predict(X_2026)
future_sales = df_2026.groupby('Manufacturer')['Predicted_2026'].mean()

# Build metrics dataframe
metrics = pd.DataFrame({'Manufacturer': past_sales.index})
metrics = metrics.set_index('Manufacturer')
metrics['Avg_2015_25'] = past_sales
metrics['Predicted_2026'] = future_sales
metrics = metrics.fillna(0)
metrics['Change'] = metrics['Predicted_2026'] - metrics['Avg_2015_25']
metrics['Change_pct'] = np.where(metrics['Avg_2015_25'] != 0,
                                   (metrics['Change'] / metrics['Avg_2015_25']) * 100,
                                   0)

# Reset index for easy lookup
metrics = metrics.reset_index()
metrics['Manufacturer'] = metrics['Manufacturer'].astype(str)

@app.route('/', methods=['GET'])
def index():
    manufacturers = sorted(metrics['Manufacturer'].unique())
    selected = request.args.get('manufacturer')
    result = None
    if selected:
        row = metrics[metrics['Manufacturer'] == selected]
        if not row.empty:
            r = row.iloc[0]
            result = {
                'Manufacturer': r['Manufacturer'],
                'Avg_2015_25': float(r['Avg_2015_25']),
                'Predicted_2026': float(r['Predicted_2026']),
                'Change': float(r['Change']),
                'Change_pct': float(r['Change_pct']),
            }
    return render_template('index.html', manufacturers=manufacturers, result=result)

@app.route('/api/metrics')
def api_metrics():
    return metrics.to_json(orient='records')


@app.route('/api/insights')
def api_insights():
    # Provide aggregated data similar to the visualizations in data.py
    try:
        # Yearly sales (average units sold per year)
        yearly = df.groupby('Year')['Units_Sold_2024'].mean().reset_index().sort_values('Year')
        yearly_sales = {'years': yearly['Year'].tolist(), 'avg_units': yearly['Units_Sold_2024'].round().astype(int).tolist()}

        # Top manufacturers by total units sold (top 10)
        top_man = (
            df.groupby('Manufacturer')['Units_Sold_2024']
              .sum()
              .sort_values(ascending=False)
              .head(10)
        )
        top_manufacturers = {'labels': top_man.index.tolist(), 'values': top_man.astype(int).tolist()}

        # Charging type vs average sales
        if 'Charging_Type' in df.columns:
            charging = df.groupby('Charging_Type')['Units_Sold_2024'].mean().round().astype(int).sort_values(ascending=False)
            charging_type = {'labels': charging.index.tolist(), 'values': charging.tolist()}
        else:
            charging_type = {'labels': [], 'values': []}

        # Country of manufacture vs avg sales (top 10)
        if 'Country_of_Manufacture' in df.columns:
            country = df.groupby('Country_of_Manufacture')['Units_Sold_2024'].mean().sort_values(ascending=False).head(10).round().astype(int)
            country_sales = {'labels': country.index.tolist(), 'values': country.tolist()}
        else:
            country_sales = {'labels': [], 'values': []}

        # Charging time by charging type
        if 'Charging_Type' in df.columns:
            charge_time = df.groupby('Charging_Type')['Charge_Time_hr'].mean().round(2).sort_values(ascending=False)
            charging_time = {'labels': charge_time.index.tolist(), 'values': charge_time.tolist()}
        else:
            charging_time = {'labels': [], 'values': []}

        return jsonify({
            'yearly_sales': yearly_sales,
            'top_manufacturers': top_manufacturers,
            'charging_type': charging_type,
            'country_sales': country_sales,
            'charging_time': charging_time
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/brand/<manufacturer>')
def api_brand(manufacturer):
    """Get year-wise sales data for a specific manufacturer"""
    try:
        brand_data = df[df['Manufacturer'] == manufacturer]
        if brand_data.empty:
            return jsonify({'error': 'Brand not found'}), 404
        
        # Year-wise sales for this brand
        yearly_brand = brand_data.groupby('Year')['Units_Sold_2024'].mean().reset_index().sort_values('Year')
        
        return jsonify({
            'years': yearly_brand['Year'].astype(int).tolist(),
            'units': yearly_brand['Units_Sold_2024'].round().astype(int).tolist()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)
