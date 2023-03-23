# IMPORTS 
import pandas as pd
import numpy as np
import os

input_file = 'data/scripts/Input_Modellierung_2023-0321_adapted.xlsx'
output_dir = 'data/scenarios/isi/'

# CO2 PRICE
df = pd.read_excel(
   io=input_file,
   sheet_name ='CO2-Price'
)
df.rename(columns={"Data source": "Source Reference"}, inplace=True)
df.to_csv(os.path.join(output_dir, "prices_co2.csv"), encoding="utf-16", index=None)

# FUEL PRICES
df = pd.read_excel(
   io=input_file,
   sheet_name ='Fuel Prices'
)
df.rename(columns={"Energie Carrier": "Component", "Datasource": "Source Reference"}, inplace=True)
df.to_csv(os.path.join(output_dir, "prices_fuels.csv"), encoding="utf-16", index=None)

# H2 SHARE
df = pd.read_excel(
   io=input_file,
   sheet_name ='Scenario Fuel-Mix Steel and Amm',
   skiprows=1
)
df.to_csv(os.path.join(output_dir, "h2share.csv"), encoding="utf-16", index=None)

# FREE ALLOCATIONS
df = pd.read_excel(
   io=input_file,
   sheet_name ='Specific Allocation',
   skiprows=1
)
df.drop(columns=['Primärschlüssel'], inplace=True)
cbam = df.iloc[:1]
df = df.iloc[1:,]
df.to_csv(os.path.join(output_dir, "free_allocations.csv"), encoding="utf-16", index=None)

cbam.drop(columns=['Industry', 'Scenario', 'Technology', 'Comment'], inplace=True)
cbam.to_csv(os.path.join(output_dir, "cbam_factor.csv"), encoding="utf-16", index=None)

