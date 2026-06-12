import pandas as pd

# Read the CSV file
df = pd.read_csv("data/fuel-prices-for-be-assessment.csv")

# Print the first 5 rows
print(df.head())

# Print the column names
print("\nColumns:")
print(df.columns.tolist())