import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# 1. Read dataset
df = pd.read_csv("C:/Users/aravi/OneDrive/Desktop/electric_vehicles_dataset.csv")
print("Original Shape:", df.shape)
print("\nNull values before cleaning:\n", df.isnull().sum())
# 2. Remove duplicate vehicles
df.drop_duplicates(subset='Vehicle_ID', inplace=True)
# 3. Separate columns
numeric_cols = [
    'Year',
    'Battery_Capacity_kWh',
    'Range_km',
    'Charge_Time_hr',
    'Price_USD',
    'CO2_Emissions_g_per_km',
    'Safety_Rating',
    'Units_Sold_2024',
    'Warranty_Years'
]

categorical_cols = [
    'Manufacturer',
    'Model',
    'Battery_Type',
    'Charging_Type',
    'Color',
    'Country_of_Manufacture',
    'Autonomous_Level'
]
# 4. Handle missing values
for col in numeric_cols:
    df[col] = df[col].fillna(df[col].median())

for col in categorical_cols:
    df[col] = df[col].fillna(df[col].mode()[0])
# 5. Fix data types
df['Year'] = df['Year'].astype(int)
df['Units_Sold_2024'] = df['Units_Sold_2024'].astype(int)
df['Warranty_Years'] = df['Warranty_Years'].astype(int)
# 6. Remove invalid values
df = df[df['Battery_Capacity_kWh'] > 0]
df = df[df['Range_km'] > 0]
df = df[df['Charge_Time_hr'] > 0]
df = df[df['Price_USD'] > 0]
df = df[df['Safety_Rating'].between(0, 5)]

# 8. Handle CO2 values (EVs → mostly zero)
df['CO2_Emissions_g_per_km'] = df['CO2_Emissions_g_per_km'].clip(lower=0)
# 9. Final validation
print("\nNull values after cleaning:\n", df.isnull().sum())
print("Final Shape:", df.shape)
# 10. Save cleaned dataset
df.to_csv("C:/Users/aravi/OneDrive/Desktop/CLEANED_EV_DATA.csv", index=False)

print("\n✅ Data cleaning completed successfully")

# 5. Descriptive Statistics

print("\nNumerical Columns Summary:")
print(df.describe())

# 6. Categorical Columns Overview

categorical_cols = df.select_dtypes(include='object').columns

for col in categorical_cols[:10]:
    print(f"\nTop values in {col}:")
    print(df[col].value_counts().head(5))

# 7. Distribution of Key Numerical Features

num_cols = [
    "Battery_Capacity_kWh", "Range_km", "Charge_Time_hr",
    "Price_USD", "Safety_Rating", "Units_Sold_2024"
]

df[num_cols].hist(bins=30, figsize=(15, 10))
plt.suptitle("Distribution of Key Numerical Features", fontsize=16)
plt.show()

# 9. Line Graph: Sales Trend by Year

yearly_sales = df.groupby("Year")["Units_Sold_2024"].mean()

plt.plot(yearly_sales.index, yearly_sales.values, marker='o')
plt.xlabel("Manufacturing Year")
plt.ylabel("Average Units Sold")
plt.title("Average Units Sold by Vehicle Year")
plt.show()


# Manufacturer Performance
top_manufacturers = (
    df.groupby("Manufacturer")["Units_Sold_2024"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

top_manufacturers.plot(kind="bar")
plt.title("Top 10 Manufacturers by Units Sold (2024)")
plt.ylabel("Units Sold")
plt.xticks(rotation=45)
plt.show()
# Charging Type vs Sales
df.groupby("Charging_Type")["Units_Sold_2024"].mean().plot(kind="bar", color="orange")
plt.title("Average Units Sold by Charging Type")
plt.ylabel("Units Sold")
plt.xticks(rotation=45)
plt.show()
# Country of Manufacture vs Sales
df.groupby("Country_of_Manufacture")["Units_Sold_2024"].mean() \
  .sort_values(ascending=False).head(10).plot(kind="bar")

plt.title("Average Units Sold by Country")
plt.ylabel("Units Sold")
plt.xticks(rotation=45)
plt.show()
# Charging Technology influences Charging Time
plt.figure(figsize=(7,5))
df.groupby("Charging_Type")["Charge_Time_hr"].mean().plot(kind="bar")
plt.xlabel("Charging Technology Type")
plt.ylabel("Average Charging Time (Hours)")
plt.title("Impact of Charging Technology on Charging Time")
plt.xticks(rotation=45)
plt.grid(axis="y")
plt.show()
#feature engineering
# Battery Efficiency (km per kWh)
df["Battery_Efficiency_km_per_kWh"] = (
    df["Range_km"] / df["Battery_Capacity_kWh"]
)
print("\nBattery_Efficiency_km_per_kWh:")
print(df["Battery_Efficiency_km_per_kWh"].head())
# Charging Efficiency (km gained per hour of charging)

df["Charging_Efficiency_km_per_hr"] = (
    df["Range_km"] / df["Charge_Time_hr"]
)
print("\nCharging_Efficiency_km_per_hr:")
print(df["Charging_Efficiency_km_per_hr"].head())
# Battery Capacity to Charging Time Ratio

df["Battery_Capacity_per_Hour"] = (
    df["Battery_Capacity_kWh"] / df["Charge_Time_hr"]
)
print("\nBattery_Capacity_per_Hour:")
print(df["Battery_Capacity_per_Hour"].head())
# Sales Efficiency (Range impact on sales)

df["Range_to_Sales_Ratio"] = (
    df["Range_km"] / (df["Units_Sold_2024"] + 1)
)
print("\nRange_to_Sales_Ratio:")
print(df["Range_to_Sales_Ratio"].head())
