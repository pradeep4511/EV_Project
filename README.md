# EV_Project
📊 Data Analytics Dashboard using Flask
📌 Project Overview

This project is a web-based data analytics dashboard developed using Python Flask. It performs end-to-end data analytics starting from data collection to model building and finally visualizes insights through an interactive web dashboard built with HTML, CSS, and JavaScript.

The goal of this project is to transform raw data into meaningful insights and make them accessible through a browser-based dashboard.

# 📂 Data Collection

Dataset was collected from Kaggle

Data is in CSV format

Contains real-world structured data suitable for analytics and prediction

Dataset includes multiple numerical and categorical attributes

# 🧹 Data Cleaning

Data cleaning was performed using Pandas and NumPy to improve data quality:

Removed duplicate records

Handled missing values (mean/median/mode as required)

Corrected inconsistent data formats

Removed irrelevant columns

Treated outliers where necessary

# 🔄 Data Processing

After cleaning, data processing steps included:

Data type conversions

Data normalization and scaling

Aggregation and grouping for analytics

Preparing datasets for visualization and modeling

# 📈 Exploratory Data Analysis (EDA)

EDA was conducted to understand patterns and trends in the data:

Statistical summaries

Distribution analysis

Correlation analysis

Trend analysis across different categories

Visualization using charts and graphs

Libraries used:

Pandas

Matplotlib

Seaborn

# 🧠 Feature Engineering

Feature engineering was applied to enhance model performance:

Encoding categorical variables

Creating derived features from existing columns

Removing multicollinearity

Feature selection based on importance

Preparing final feature set for modeling

# 🤖 Model Building

Machine learning models were built using Scikit-learn:

Train-test split applied

Models trained on processed data

Performance evaluated using metrics such as:

R² Score

Mean Absolute Error (MAE)

Best-performing model selected for deployment

# 🎨 Frontend Development (HTML, CSS, JavaScript)

Frontend interface was built using:

HTML for structure

CSS for styling and layout

JavaScript for interactivity

Features:

Clean and responsive UI

Interactive charts and tables

Dropdowns and buttons for user interaction

# ⚙️ Flask Application Development (app.py)

The backend of the project was developed using Flask:

Created routes for dashboard and analytics pages

Integrated data processing and model logic

Passed dynamic data to frontend using Jinja2

Handled user inputs and responses


# 📊 Dashboard Development

The dashboard visualizes key insights and analytics:

Summary KPIs

Trend analysis charts

Category-wise comparisons

Model prediction outputs (if applicable)

User-friendly navigation

Charts were rendered directly in the browser using dynamic data from Flask.

# 🛠️ Technologies Used

Python

Pandas

NumPy

Scikit-learn

Matplotlib / Seaborn
Flask

HTML

CSS

JavaScript

