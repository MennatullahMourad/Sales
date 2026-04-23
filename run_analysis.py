"""
Executable script version of the analysis to generate all visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# Create images directory
os.makedirs('images', exist_ok=True)

# Configure style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11

colors = ['#2E4057', '#048A81', '#54C6EB', '#8A89C0', '#CDA7C7']
sns.set_palette(colors)

# Load data
df = pd.read_csv('sales_data_raw.csv')
print(f'Loaded: {df.shape}')

# Data Cleaning
df = df.drop_duplicates()

categorical_cols = ['Customer_Segment', 'Region', 'Shipping_Mode']
for col in categorical_cols:
    mode_value = df[col].mode()[0]
    df[col] = df[col].fillna(mode_value)

def parse_date(date_str):
    try:
        return pd.to_datetime(date_str, format='%Y-%m-%d')
    except:
        try:
            return pd.to_datetime(date_str, format='%d/%m/%Y')
        except:
            return pd.NaT

df['Order_Date'] = df['Order_Date'].apply(parse_date)

text_cols = ['Region', 'Customer_Segment', 'Category', 'Product', 'Shipping_Mode']
for col in text_cols:
    df[col] = df[col].str.strip().str.title()

df['Year'] = df['Order_Date'].dt.year
df['Month'] = df['Order_Date'].dt.month
df['Month_Name'] = df['Order_Date'].dt.month_name()
df['Day_of_Week'] = df['Order_Date'].dt.day_name()
df['Quarter'] = df['Order_Date'].dt.quarter
df['Profit_Margin'] = (df['Profit'] / df['Sales'] * 100).round(2)

print(f'Cleaned: {df.shape}')

# ============ VIZ 1: Sales by Category ============
category_sales = df.groupby('Category').agg({
    'Sales': 'sum', 'Profit': 'sum', 'Order_ID': 'count'
}).round(2).sort_values('Sales', ascending=False)
category_sales.columns = ['Total Sales', 'Total Profit', 'Number of Orders']

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
category_sales['Total Sales'].plot(kind='bar', ax=axes[0], color=colors[0], edgecolor='black')
axes[0].set_title('Total Sales by Category', fontsize=14, fontweight='bold', pad=15)
axes[0].set_xlabel('Category', fontsize=12)
axes[0].set_ylabel('Total Sales ($)', fontsize=12)
axes[0].tick_params(axis='x', rotation=45)
axes[0].grid(axis='y', alpha=0.3)
for i, v in enumerate(category_sales['Total Sales']):
    axes[0].text(i, v + 50000, f'${v/1000:.0f}K', ha='center', fontsize=10, fontweight='bold')

axes[1].pie(category_sales['Total Sales'], labels=category_sales.index,
            autopct='%1.1f%%', colors=colors, startangle=90,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2})
axes[1].set_title('Sales Distribution by Category', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig('images/01_sales_by_category.png', dpi=100, bbox_inches='tight')
plt.close()
print('Saved: 01_sales_by_category.png')

# ============ VIZ 2: Monthly Trend ============
monthly_sales = df.groupby(df['Order_Date'].dt.to_period('M'))['Sales'].sum()
monthly_sales.index = monthly_sales.index.to_timestamp()

fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(monthly_sales.index, monthly_sales.values, marker='o',
        linewidth=2.5, markersize=8, color=colors[1])
ax.fill_between(monthly_sales.index, monthly_sales.values, alpha=0.2, color=colors[1])
ax.set_title('Monthly Sales Trend (2023-2024)', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=12)
ax.set_ylabel('Total Sales ($)', fontsize=12)
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('images/02_monthly_trend.png', dpi=100, bbox_inches='tight')
plt.close()
print('Saved: 02_monthly_trend.png')

# ============ VIZ 3: Top Products ============
top_products = df.groupby('Product')['Sales'].sum().sort_values(ascending=False).head(10)

fig, ax = plt.subplots(figsize=(12, 7))
ax.barh(top_products.index[::-1], top_products.values[::-1],
        color=colors[2], edgecolor='black')
ax.set_title('Top 10 Best-Selling Products', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Total Sales ($)', fontsize=12)
ax.set_ylabel('Product', fontsize=12)
ax.grid(axis='x', alpha=0.3)
for i, v in enumerate(top_products.values[::-1]):
    ax.text(v + 5000, i, f'${v/1000:.1f}K', va='center', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('images/03_top_products.png', dpi=100, bbox_inches='tight')
plt.close()
print('Saved: 03_top_products.png')

# ============ VIZ 4: Sales by Region ============
region_analysis = df.groupby('Region').agg({
    'Sales': 'sum', 'Profit': 'sum', 'Order_ID': 'count'
}).round(2).sort_values('Sales', ascending=False)
region_analysis.columns = ['Total Sales', 'Total Profit', 'Number of Orders']

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(region_analysis))
width = 0.35
ax.bar(x - width/2, region_analysis['Total Sales']/1000, width,
       label='Sales ($K)', color=colors[0], edgecolor='black')
ax.bar(x + width/2, region_analysis['Total Profit']/1000, width,
       label='Profit ($K)', color=colors[1], edgecolor='black')
ax.set_title('Sales and Profit by Region', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Region', fontsize=12)
ax.set_ylabel('Amount (Thousand $)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(region_analysis.index)
ax.legend()
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('images/04_sales_by_region.png', dpi=100, bbox_inches='tight')
plt.close()
print('Saved: 04_sales_by_region.png')

# ============ VIZ 5: Heatmap ============
pivot_table = df.pivot_table(values='Sales', index='Category',
                              columns='Region', aggfunc='sum').round(2)

fig, ax = plt.subplots(figsize=(12, 7))
sns.heatmap(pivot_table, annot=True, fmt=',.0f', cmap='YlGnBu',
            linewidths=1, linecolor='white', cbar_kws={'label': 'Sales ($)'}, ax=ax)
ax.set_title('Sales Heatmap: Category vs Region', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Region', fontsize=12)
ax.set_ylabel('Category', fontsize=12)
plt.tight_layout()
plt.savefig('images/05_heatmap.png', dpi=100, bbox_inches='tight')
plt.close()
print('Saved: 05_heatmap.png')

# ============ VIZ 6: Discount Impact ============
discount_analysis = df.groupby('Discount').agg({
    'Sales': 'sum', 'Profit': 'sum', 'Order_ID': 'count'
}).round(2)
discount_analysis.columns = ['Total Sales', 'Total Profit', 'Number of Orders']

fig, ax = plt.subplots(figsize=(12, 6))
ax2 = ax.twinx()
ax.bar(discount_analysis.index.astype(str), discount_analysis['Total Sales'],
       color=colors[0], alpha=0.7, edgecolor='black', label='Sales')
ax2.plot(discount_analysis.index.astype(str), discount_analysis['Total Profit'],
         color=colors[3], marker='o', linewidth=2.5, markersize=10, label='Profit')
ax.set_title('Impact of Discount on Sales and Profit', fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Discount Rate', fontsize=12)
ax.set_ylabel('Total Sales ($)', fontsize=12, color=colors[0])
ax2.set_ylabel('Total Profit ($)', fontsize=12, color=colors[3])
ax.legend(loc='upper left')
ax2.legend(loc='upper right')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('images/06_discount_impact.png', dpi=100, bbox_inches='tight')
plt.close()
print('Saved: 06_discount_impact.png')

# ============ VIZ 7: Customer Segment ============
segment_analysis = df.groupby('Customer_Segment').agg({
    'Sales': 'sum', 'Profit': 'sum', 'Order_ID': 'count', 'Customer_ID': 'nunique'
}).round(2)
segment_analysis.columns = ['Total Sales', 'Total Profit', 'Orders', 'Unique Customers']

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
axes[0].pie(segment_analysis['Total Sales'], labels=segment_analysis.index,
            autopct='%1.1f%%', colors=colors, startangle=90,
            wedgeprops={'edgecolor': 'white', 'linewidth': 2})
axes[0].set_title('Sales by Customer Segment', fontsize=14, fontweight='bold', pad=15)

segment_analysis['Orders'].plot(kind='bar', ax=axes[1], color=colors[2], edgecolor='black')
axes[1].set_title('Number of Orders by Segment', fontsize=14, fontweight='bold', pad=15)
axes[1].set_xlabel('Customer Segment', fontsize=12)
axes[1].set_ylabel('Number of Orders', fontsize=12)
axes[1].tick_params(axis='x', rotation=0)
axes[1].grid(axis='y', alpha=0.3)
for i, v in enumerate(segment_analysis['Orders']):
    axes[1].text(i, v + 20, f'{v}', ha='center', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig('images/07_segment_analysis.png', dpi=100, bbox_inches='tight')
plt.close()
print('Saved: 07_segment_analysis.png')

# Save cleaned data
df.to_csv('sales_data_cleaned.csv', index=False)
print(f'\nCleaned data saved: {df.shape}')

# Print key stats for README
print('\n' + '='*50)
print('KEY STATISTICS')
print('='*50)
print(f'Total Sales: ${df["Sales"].sum():,.2f}')
print(f'Total Profit: ${df["Profit"].sum():,.2f}')
print(f'Total Orders: {len(df):,}')
print(f'Unique Customers: {df["Customer_ID"].nunique():,}')
print(f'Profit Margin: {(df["Profit"].sum() / df["Sales"].sum() * 100):.2f}%')
