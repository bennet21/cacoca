# IMPORTS
import pandas as pd
import os

# input_file = 'scripts/data/Input_Modellierung_2023-0321_adapted.xlsx'
# output_dir = 'data/scenarios/isi/'
input_file = 'scripts/data/Tool_ALL.xlsm'
output_dir = 'data/scenarios/isi_all/'

# ======= CHANGES TO EXCEL FILE: =======
# - CO2-Price: none
# - fuel prices: move down "datasource", delete AM2-AS65, delete B64, delete A48-A52
# - Fuel-Mix: delete b34
# - specific allocation: add column name "Comment" in AI2
# - Projects: rename columns:
#     Project size/Production capacity [Mt/a] or GW
#     Share of high CAPEX
#     H2 Share Scenario


# CO2 PRICE
df = pd.read_excel(
   io=input_file,
   sheet_name ='CO2-Price',
   skiprows=3
)
df.rename(columns={"Data source": "Source Reference"}, inplace=True)
df.to_csv(os.path.join(output_dir, "prices_co2.csv"), encoding="utf-16", index=None)

# FUEL PRICES
df = pd.read_excel(
   io=input_file,
   sheet_name ='Fuel Prices',
   skiprows=1
)
df.rename(columns={"Energie Carrier": "Component", "Datasource": "Source Reference"}, inplace=True)
df = df[~df['Component'].isnull()]
df.to_csv(os.path.join(output_dir, "prices_fuels.csv"), encoding="utf-16", index=None)

# H2 SHARE
df = pd.read_excel(
   io=input_file,
   sheet_name ='Scenario Fuel-Mix Steel and Amm',
   skiprows=2,

)
df = df[~df['Scenario'].isnull()]
df = df.drop(columns=["Steel"])
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
df.rename(columns={"Szenario": "Scenario"}, inplace=True)
df = df[~df['Scenario'].isnull()]
df.to_csv(os.path.join(output_dir, "free_allocations.csv"), encoding="utf-16", index=None)

cbam.drop(columns=['Industry', 'Szenario', 'Technology', 'Comment'], inplace=True)
cbam.to_csv(os.path.join(output_dir, "cbam_factor.csv"), encoding="utf-16", index=None)

