# IMPORTS --------------------------------------------------
import pandas as pd
import numpy as np
# TECHNOLOGY PARAMETER SHEET -------------------------------
# read in technology param inverted sheet
techparam = pd.read_excel(
   io='Input_Modellierung_2023-0321.xlsx',
   sheet_name ='Technology Parameter inverted'
)
# remove first rows
techparam = techparam.iloc[2:,]

# rename column names
techparam.columns = ['Index', 'Industry', 'Technology', 'Datasource', 'Reference Technology',
       'Unit', 'CO2','Natural Gas','Electricity','Hydrogen' ,
       'Coking Coal','Injection Carbon','Iron ore','Scrap Steel',
       'DRI-Pellets','Naphta','Additional OPEX','Steel: DRI- Alternative Tech (Fuel)',
       'Technology Benchmark','Kommentar',
       'Unused_1', 'Technology_2','Energy Intensity', 'Factor',
       'Natural Gas_2', 'Electricity_2', 'Hydrogen_2',
       'Coking Coal_2', 'Injection Carbon_2', 'Iron ore_2', 'Scrap Steel_2',
       'DRI-Pellets_2', 'Naphta_2', 'Unnamed: 33', 'Unnamed: 34', 'Hydrogen .1',
       'Coking Coal.1', 'Injection Carbon.1', 'Naphta.1']

# melt down dataframe to create desired format
# the columns for the melted dataframe are all selected here (lots of the original columns are not needed)
techparam_primary = pd.melt(techparam, id_vars=['Industry', 'Technology', 'Datasource', 'Reference Technology','Technology Benchmark','Kommentar'],
                  value_vars=['CO2','Natural Gas','Electricity','Hydrogen' ,
       'Coking Coal','Injection Carbon','Iron ore','Scrap Steel',
       'DRI-Pellets','Naphta','Additional OPEX','Steel: DRI- Alternative Tech (Fuel)'],
        var_name='variable', value_name='value')

# filter out NaN values
techparam_filtered = techparam_primary[~techparam_primary['value'].isnull()]

# append Units (The units are not stored as a column in the excel file)
units_dict = {'CO2': 't/t RS', 'Natural Gas': 'MWh/t RS', 'Electricity': 'MWh/t RS',
               'Hydrogen': 'kg/t RS', 'Coking Coal': 't/t RS', 'Injection Carbon': 't/t RS',
               'Iron ore': 't/t RS', 'Scrap Steel': 't/t RS', 'DRI-Pellets': 't/t RS',
               'Naphta': 't/t RS', 'Additional OPEX': '€/t RS',
               'Steel: DRI- Alternative Tech (Fuel)': 'na'}

techparam_filtered['unit'] = techparam_filtered['variable'].map(units_dict)

print(techparam_filtered.columns)

# rename the columns of the final dataframe
techparam_filtered.columns = ['Industry', 'Technology', 'Source Reference', 'Reference Technology',
       'Technology Benchmark', 'Comment', 'Energy Carrier/Feedstock', 'Reported Value', 'Reported Unit']

# add missing columns
techparam_filtered['Reported Uncertainty'] = np.nan
techparam_filtered['Period'] = np.nan

# reorder the columns
techparam_filtered = techparam_filtered[['Industry', 'Technology' , 'Reference Technology',
       'Technology Benchmark', 'Energy Carrier/Feedstock', 'Reported Value', 'Reported Uncertainty',
       'Reported Unit', 'Source Reference', 'Comment']]



# write the result to a csv file
techparam_filtered.to_csv("techparam_unsensitive.csv", encoding="utf-16", index=None)
