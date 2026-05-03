import pandas as pd
df = pd.read_csv('fuel-prices-for-be-assessment.csv')
print(f"Total Rows: {len(df)}")
print(f"Unique OPIS IDs: {df['OPIS Truckstop ID'].nunique()}")
print(f"Unique Addresses: {df['Address'].nunique()}")
print(f"Unique City/State combos: {len(df.groupby(['City', 'State']))}")
