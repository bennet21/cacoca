import pandas as pd 
import os


class ScenarioData(): 
    def __init__(self, prices, free_allocations): 
        self.prices = prices 
        self.free_allocations = free_allocations 


def read_scenario_data(dirpath: str, scenarios_actual: dict, scenarios_bidding: dict): 
    data_all, h2share, cbam_factor = read_all_scenario_data(dirpath=dirpath)
    data_actual = choose_by_scenario_dict(data_all, scenarios_actual)
    data_bidding = choose_by_scenario_dict(data_all, scenarios_bidding)
    return data_actual, data_bidding, h2share, cbam_factor


def read_all_scenario_data(dirpath: str):
    co2prices = pd.read_csv(os.path.join(dirpath,'prices_co2.csv'), encoding="utf-16")
    co2prices.insert(0, 'Component', 'CO2', True) 
    fuel_prices = pd.read_csv(os.path.join(dirpath,'prices_fuels.csv'), encoding="utf-16")
    prices = pd.concat([co2prices, fuel_prices])
    h2share = pd.read_csv(os.path.join(dirpath,'h2share.csv'), encoding="utf-16")
    free_allocations = pd.read_csv(os.path.join(dirpath,'free_allocations.csv'), encoding="utf-16")
    cbam_factor = pd.read_csv(os.path.join(dirpath,'cbam_factor.csv'), encoding="utf-16")
    return ScenarioData(prices, free_allocations), h2share, cbam_factor


def choose_by_scenario_dict(data_all, scenarios: dict):
    prices = pd.concat([
        data_all.prices.query(f"Component=='{component.replace('Prices ', '')}'") \
            .query(f"Scenario=='{scenario}'") \
            .drop(columns=["Scenario"]) \
        for component, scenario in scenarios.items() if component.startswith("Prices ")
    ])
    
    free_allocations = data_all.free_allocations \
        .query(f"Scenario=='{scenarios['Free Allocations']}'") \
        .drop(columns=["Scenario"])
    
    return ScenarioData(prices, free_allocations)
    
    
