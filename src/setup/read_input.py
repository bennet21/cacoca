import yaml
import os
import numpy as np
import pandas as pd
from src.setup.select_scenario_data import ScenarioData


def read_config(filepath: str):
    with open(filepath, 'r') as f:
        file_content = f.read()
    config = yaml.load(file_content, Loader=yaml.CLoader)
    config['years'] = np.arange(config['start_year'], config['end_year'] + 1)
    return config


def read_projects(filepath: str, default_wacc: float):
    projects = pd.read_excel(filepath, sheet_name='Projects')
    projects = projects.query("Active == 1")
    projects = projects.fillna({'WACC': default_wacc})
    return projects


def read_techdata(dir_path: str, filenames_base: list):
    techdata = [
        pd.read_csv(
            os.path.join(dir_path, fnb + '.csv')
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


def read_raw_scenario_data(dirpath: str):
    co2prices = pd.read_csv(os.path.join(dirpath, 'prices_co2.csv'), encoding="utf-16")
    co2prices.insert(0, 'Component', 'CO2', True)
    fuel_prices = pd.read_csv(os.path.join(dirpath, 'prices_fuels.csv'), encoding="utf-16")
    prices = pd.concat([co2prices, fuel_prices])
    h2share = pd.read_csv(os.path.join(dirpath, 'h2share.csv'), encoding="utf-16")
    free_allocations = pd.read_csv(os.path.join(dirpath, 'free_allocations.csv'), encoding="utf-16")
    # cbam_factor = pd.read_csv(os.path.join(dirpath,'cbam_factor.csv'), encoding="utf-16")
    return ScenarioData(prices, free_allocations), h2share
