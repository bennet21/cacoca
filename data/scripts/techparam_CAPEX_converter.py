# IMPORTS ----------------------------------------------------------------
import pandas as pd
import numpy as np
import os
# CONFIG -----------------------------------------------------------------
# input_file = 'data/scripts/Input_Modellierung_2023-0321_adapted.xlsx'
# output_dir = 'data/tech/isi/'
input_file = 'data/scripts/Tool_ALL.xlsm'
output_dir = 'data/tech/isi_all/'

# BEGIN READING TECHNOLOGY PARAMETER SHEET -------------------------------
# read in technology param inverted sheet
techparam = pd.read_excel(
   io = input_file,
   sheet_name ='Technology Parameter inverted'
)
# remove first rows
techparam = techparam.iloc[2:,]

# rename column names
techparam.columns = ['Index', 'Industry', 'Technology', 'Datasource', 'Reference Technology',
       'Unit', 'CO2','Natural Gas','Electricity','Hydrogen' ,
       'Coking Coal','Injection Coal','Iron Ore','Scrap Steel',
       'DRI-Pellets','Naphta','Additional OPEX','Steel: DRI- Alternative Tech (Fuel)',
       'Technology Benchmark','Kommentar',
       'Unused_1', 'Technology_2','Energy Intensity', 'Factor',
       'Natural Gas_2', 'Electricity_2', 'Hydrogen_2',
       'Coking Coal_2', 'Injection Coal_2', 'Iron Ore_2', 'Scrap Steel_2',
       'DRI-Pellets_2', 'Naphta_2', 'Unnamed: 33', 'Unnamed: 34', 'Hydrogen .1',
       'Coking Coal.1', 'Injection Coal.1', 'Naphta.1']

# BEGIN TECHNOLOGY MAPPING CSV -------------------------------
# creata a mapping dataframe for technology to reference technology
tech_mapping = techparam[['Technology', 'Reference Technology']]

# filter out NaN values
tech_mapping_filtered = tech_mapping[~tech_mapping['Technology'].isnull()]

# write technology mapping to csv file
tech_mapping_filtered.to_csv(os.path.join(output_dir, "technology_reference_mapping.csv"), encoding="utf-16", index=None)
# END TECHNOLOGY MAPPING CSV -------------------------------

# melt down dataframe to create desired format
# the columns for the melted dataframe are all selected here (lots of the original columns are not needed)
techparam_primary = pd.melt(techparam, id_vars=['Industry', 'Technology', 'Datasource','Kommentar'],
                  value_vars=['CO2','Natural Gas','Electricity','Hydrogen' ,
       'Coking Coal','Injection Coal','Iron Ore','Scrap Steel',
       'DRI-Pellets','Naphta','Additional OPEX'],
        var_name='variable', value_name='value')

# filter out NaN values
techparam_filtered = techparam_primary[~techparam_primary['value'].isnull() & ~techparam_primary['Industry'].isnull()]

# append Units (The units are not stored as a column in the excel file)
units_dict = {'CO2': 't/t RS', 'Natural Gas': 'MWh/t RS', 'Electricity': 'MWh/t RS',
               'Hydrogen': 'kg/t RS', 'Coking Coal': 't/t RS', 'Injection Coal': 't/t RS',
               'Iron Ore': 't/t RS', 'Scrap Steel': 't/t RS', 'DRI-Pellets': 't/t RS',
               'Naphta': 't/t RS', 'Additional OPEX': '€/t RS'}

techparam_filtered = techparam_filtered.assign(unit = techparam_filtered['variable'].map(units_dict))

# append Type
units_dict = {'CO2': 'Emissions', 'Natural Gas': 'Energy demand', 'Electricity': 'Energy demand',
               'Hydrogen': 'Energy demand', 'Coking Coal': 'Energy demand', 'Injection Coal': 'Energy demand',
               'Iron Ore': 'Feedstock demand', 'Scrap Steel': 'Feedstock demand', 'DRI-Pellets': 'Feedstock demand',
               'Naphta': 'Feedstock demand', 'Additional OPEX': 'OPEX'}

techparam_filtered = techparam_filtered.assign(type = techparam_filtered['variable'].map(units_dict))

# add missing columns
techparam_filtered = techparam_filtered.assign(Subcomponent = np.nan,
                               Region = np.nan,
                               Period = np.nan,
                               Usage = np.nan,
                               Uncertainty = np.nan,
                               Non_unit_conversion_factor = np.nan,
                               Mode = np.nan,
                               Source_comment = np.nan)

# rename the columns of the final dataframe
techparam_filtered.columns = ['Industry', 'Technology', 'Source reference', 'Value and uncertainty comment',
                              'Component', 'Value', 'Unit', "Type",
                              'Subcomponent','Region','Period',
                              'Usage','Uncertainty',
                              'Non-unit conversion factor','Mode','Source comment']

# END READING TECHNOLOGY PARAMETER SHEET -------------------------------

# BEGIN READING CAPEX TECHNOLOGY ---------------------------------------
# read in excel sheet
capextech = pd.read_excel(
   io=input_file,
   sheet_name ='CAPEX Technology '
)
# remove first row and all columns after 6
capextech = capextech.iloc[2:,:6]

# rename columns
capextech.columns = ['Technology',
       'Industry', 'Source reference', 'Scenario', 'Unit', 'Value']

# fill in missing technology values with value from previous row (due to the structure of the excel sheet)
capextech['Technology'].fillna(method='ffill', inplace=True)

# filter out row with missing scenario or value
capextech = capextech[~capextech['Scenario'].isnull() & ~capextech['Value'].isnull() & ~(capextech['Value'] == 0)]

# add Type, Component and Mode column
capextech =  capextech.assign(Component = "CAPEX",
                              Value_and_uncertainty_comment = np.nan,
                              Type = np.nan)

# rename columns
capextech.columns = ['Technology',
       'Industry', 'Source reference', 'Scenario', 'Unit', 'Value',
       'Component', 'Value and uncertainty comment', 'Type',]

# fill Type column
# Set values to 'High CAPEX' for rows where Scenario ends with "_High"
capextech.loc[capextech['Scenario'].str.endswith('_High'), 'Type'] = 'High CAPEX'

# Set values to 'Low CAPEX' for rows where Scenario ends with "_Low"
capextech.loc[capextech['Scenario'].str.endswith('_Low'), 'Type'] = 'Low CAPEX'

# reorder columns to match techparam dataframe
capextech = capextech[['Industry', 'Technology', 'Source reference', 'Value and uncertainty comment',
                              'Component', 'Value', 'Unit', "Type"]]

# add missing columns
capextech = capextech.assign(Subcomponent = np.nan,
                               Region = np.nan,
                               Period = 2022,
                               Usage = np.nan,
                               Uncertainty = np.nan,
                               Non_unit_conversion_factor = np.nan,
                               Mode = np.nan,
                               Source_comment = np.nan)

# rename the columns of the final dataframe
capextech.columns = ['Industry', 'Technology', 'Source reference', 'Value and uncertainty comment',
                              'Component', 'Value', 'Unit', "Type",
                              'Subcomponent','Region','Period',
                              'Usage','Uncertainty',
                              'Non-unit conversion factor','Mode','Source comment']

# END READING CAPEX TECHNOLOGY -------------------------------

# BEGIN JOIN TWO DATAFRAMES ----------------------------------

# columns are the same at this point, so the two dataframes can easily be concatenated
all_params = pd.concat([capextech, techparam_filtered])

# END JOIN TWO DATAFRAMES ------------------------------------

# BEGIN WRITE RESULTS ----------------------------------------
# reorder the columns
all_params = all_params[['Industry','Technology','Mode','Type','Component',
       'Subcomponent','Region','Period','Usage','Value','Uncertainty',
       'Unit','Non-unit conversion factor','Value and uncertainty comment','Source reference','Source comment']]

# strip industry values
all_params['Industry'] = all_params['Industry'].str.strip()

# iterate over all industries and create a coresponding csv file with the matching data entries
for industry in all_params.Industry.unique():
       # Get the rows that have the current industry in the industry column
       industry_rows = all_params[all_params['Industry'] == industry]

       # delete Industry column
       industry_rows = industry_rows.drop("Industry", axis=1)

       # Write the rows to a csv file with the same name as the industry
       filename = str(industry).lower().replace(" ", "_") + ".csv"
       industry_rows.to_csv(os.path.join(output_dir, filename), index=False)

# END WRITE RESULTS ------------------------------------------