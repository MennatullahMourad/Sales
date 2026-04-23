"""
Script to generate realistic sales data with common real-world issues
(missing values, duplicates, inconsistent formats) for the analysis project.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

# Product categories and subcategories
products = {
    'Electronics': ['Laptop', 'Smartphone', 'Headphones', 'Tablet', 'Smartwatch'],
    'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Shoes', 'Dress'],
    'Home & Kitchen': ['Coffee Maker', 'Blender', 'Cookware Set', 'Vacuum', 'Air Fryer'],
    'Books': ['Novel', 'Textbook', 'Biography', 'Cookbook', 'Self-Help'],
    'Sports': ['Yoga Mat', 'Dumbbells', 'Running Shoes', 'Bicycle', 'Tennis Racket']
}

regions = ['North', 'South', 'East', 'West', 'Central']
customer_segments = ['Consumer', 'Corporate', 'Home Office']
shipping_modes = ['Standard', 'Express', 'Same Day', 'First Class']

# Generate base data
n_records = 2500
data = []

start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)

for i in range(n_records):
    category = random.choice(list(products.keys()))
    product = random.choice(products[category])
    
    # Price based on category
    price_ranges = {
        'Electronics': (200, 2000),
        'Clothing': (20, 300),
        'Home & Kitchen': (50, 800),
        'Books': (10, 80),
        'Sports': (25, 1500)
    }
    unit_price = round(random.uniform(*price_ranges[category]), 2)
    quantity = random.randint(1, 10)
    discount = round(random.choice([0, 0, 0, 0.1, 0.15, 0.2, 0.25]), 2)
    
    sales = round(unit_price * quantity * (1 - discount), 2)
    profit = round(sales * random.uniform(0.05, 0.35), 2)
    
    random_days = random.randint(0, (end_date - start_date).days)
    order_date = start_date + timedelta(days=random_days)
    
    record = {
        'Order_ID': f'ORD-{10000 + i}',
        'Order_Date': order_date.strftime('%Y-%m-%d'),
        'Customer_ID': f'CUST-{random.randint(1000, 1500)}',
        'Customer_Segment': random.choice(customer_segments),
        'Region': random.choice(regions),
        'Category': category,
        'Product': product,
        'Quantity': quantity,
        'Unit_Price': unit_price,
        'Discount': discount,
        'Sales': sales,
        'Profit': profit,
        'Shipping_Mode': random.choice(shipping_modes)
    }
    data.append(record)

df = pd.DataFrame(data)

# Introduce realistic data issues
# 1. Missing values
missing_indices = np.random.choice(df.index, size=80, replace=False)
df.loc[missing_indices[:30], 'Customer_Segment'] = np.nan
df.loc[missing_indices[30:55], 'Shipping_Mode'] = np.nan
df.loc[missing_indices[55:], 'Region'] = np.nan

# 2. Duplicate rows
duplicate_rows = df.sample(n=25, random_state=1)
df = pd.concat([df, duplicate_rows], ignore_index=True)

# 3. Inconsistent date formats
inconsistent_dates = np.random.choice(df.index, size=50, replace=False)
for idx in inconsistent_dates[:25]:
    date_obj = datetime.strptime(df.loc[idx, 'Order_Date'], '%Y-%m-%d')
    df.loc[idx, 'Order_Date'] = date_obj.strftime('%d/%m/%Y')

# 4. Inconsistent capitalization in Region
cap_indices = np.random.choice(df.index, size=60, replace=False)
for idx in cap_indices[:20]:
    if pd.notna(df.loc[idx, 'Region']):
        df.loc[idx, 'Region'] = df.loc[idx, 'Region'].upper()
for idx in cap_indices[20:40]:
    if pd.notna(df.loc[idx, 'Region']):
        df.loc[idx, 'Region'] = df.loc[idx, 'Region'].lower()

# 5. Shuffle and save
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv('sales_data_raw.csv', index=False)

print(f"Generated {len(df)} records")
print(f"Missing values:\n{df.isnull().sum()}")
print(f"Duplicates: {df.duplicated().sum()}")
print(f"\nFirst few rows:")
print(df.head())
