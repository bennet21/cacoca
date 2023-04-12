import pandas as pd
import os


class ScenarioData():
    def __init__(self, prices: pd.DataFrame, free_allocations: pd.DataFrame):
        self.prices = prices
        self.free_allocations = free_allocations


def read_scenario_data(dirpath: str, scenarios_actual: dict,
                       scenarios_bidding: dict, projects: pd.DataFrame):
    data_all, h2share = read_all_scenario_data(dirpath=dirpath)
    data_actual = choose_by_scenario_dict(data_all, scenarios_actual)
    data_bidding = choose_by_scenario_dict(data_all, scenarios_bidding)
    h2share = choose_by_projects(h2share, projects)

    data_actual.prices = years_to_rows(
        data_actual.prices, year_name="Period", value_name="Price"
    )
    add_variance(data_actual.prices, mode='h2_and_co2_sigma0.2')

    data_actual.free_allocations = years_to_rows(
        data_actual.free_allocations, year_name="Period", value_name="Free Allocations"
    )

    data_bidding.prices = years_to_rows(
        data_bidding.prices, year_name="Period", value_name="Price"
    )
    add_variance(data_bidding.prices, mode='h2_and_co2_sigma0.2')

    data_bidding.free_allocations = years_to_rows(
        data_bidding.free_allocations, year_name="Period", value_name="Free Allocations"
    )

    h2share = years_to_rows(h2share, year_name="Operation Year", value_name="H2 Share") \
        .assign(Period=lambda df: df['Operation Year'] + df['Time of investment'] - 1) \
        .drop(columns=['Operation Year', 'Time of investment'])

    return data_actual, data_bidding, h2share


def read_all_scenario_data(dirpath: str):
    co2prices = pd.read_csv(os.path.join(dirpath, 'prices_co2.csv'), encoding="utf-16")
    co2prices.insert(0, 'Component', 'CO2', True)
    fuel_prices = pd.read_csv(os.path.join(dirpath, 'prices_fuels.csv'), encoding="utf-16")
    prices = pd.concat([co2prices, fuel_prices])
    h2share = pd.read_csv(os.path.join(dirpath, 'h2share.csv'), encoding="utf-16")
    free_allocations = pd.read_csv(os.path.join(dirpath, 'free_allocations.csv'), encoding="utf-16")
    # cbam_factor = pd.read_csv(os.path.join(dirpath,'cbam_factor.csv'), encoding="utf-16")
    return ScenarioData(prices, free_allocations), h2share


def choose_by_scenario_dict(data_all: ScenarioData, scenarios: dict):
    prices = pd.concat([
        data_all.prices.query(f"Component=='{component.replace('Prices ', '')}'")
        .query(f"Scenario=='{scenario}'")
        .drop(columns=["Scenario"])
        for component, scenario in scenarios.items() if component.startswith("Prices ")
    ])

    free_allocations = data_all.free_allocations \
        .query(f"Scenario=='{scenarios['Free Allocations']}'") \
        .drop(columns=["Scenario"])

    return ScenarioData(prices, free_allocations)


def choose_by_projects(h2share: pd.DataFrame, projects: pd.DataFrame):
    return projects \
        .filter(['Project name', 'Time of investment', 'H2 Share Scenario']) \
        .merge(
            h2share,
            how='left',
            left_on='H2 Share Scenario',
            right_on='Scenario'
        ) \
        .drop(columns=['H2 Share Scenario', 'Scenario'])


def years_to_rows(data: pd.DataFrame, year_name: str, value_name: str):
    years = [str(x) for x in data.columns if str(x).isdigit()]
    id_vars = [str(x) for x in data.columns if not str(x).isdigit()]
    data = data.melt(
        id_vars=id_vars,
        value_vars=years,
        var_name=year_name,
        value_name=value_name
    )
    data[year_name] = data[year_name].astype(int)
    return data


def add_variance(prices: pd.DataFrame, mode: str):
    if mode == 'h2_and_co2_sigma0.2':
        prices.insert(loc=len(prices.columns),
                      column='Price_variance', value=0.)

        for component in ['Hydrogen']:
            h2rows = prices["Component"] == component
            prices.loc[h2rows, 'Price_variance'] \
                = (0.2 * prices.loc[h2rows, 'Price'])**2
        for component in ['CO2']:
            h2rows = prices["Component"] == component
            prices.loc[h2rows, 'Price_variance'] \
                = (0.2 * prices.loc[h2rows, 'Price'])**2
    else:
        raise Exception(f"Invalid mode '{mode}'.")
