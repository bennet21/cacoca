import pandas as pd 
import numpy as np
import os

column_list = ['Technology', 
                'Mode', 
                'Type', 
                'Component', 
                'Subcomponent', 
                'Region', 
                'Period', 
                'Usage', 
                'Reported value', 
                'Reported uncertainty', 
                'Reported unit', 
                'Non-unit conversion factor', 
                'Used value', 
                'Used uncertainty', 
                'Used unit', 
                'Value and uncertainty comment', 
                'Source reference', 
                'Source comment']

def read(dir_path: str, filenames_base: list):
    techdata = [
        pd.read_csv(
            os.path.join(dir_path, fnb+'.csv')#, 
            #names = column_list
            ) for fnb in filenames_base 
    ]
    for df, fnb in zip(techdata, filenames_base): 
        df.insert(0, "Industry", fnb, True)
    techdata = pd.concat(techdata)

    reference_tech = pd.read_csv(
        os.path.join(dir_path, 'technology_reference_mapping.csv'), 
        encoding="utf-16"
        ) 

    return techdata, reference_tech

def expand_by_years(techdata: pd.DataFrame, years: np.ndarray): 
    years_df = pd.DataFrame.from_dict({'Period': years})
    techdata = techdata.drop(columns=['Period']).merge(years_df, how='cross')
    return techdata
    