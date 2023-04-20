import pandas as pd


def select_prices(prices: pd.DataFrame, scenarios: dict):

    prices = choose_by_scenario_dict(prices, scenarios['prices'])
    prices = years_to_rows(prices, year_name="Period", value_name="Price")

    return prices


def select_free_allocations(free_allocations: pd.DataFrame, scenarios: dict):

    free_allocations = choose_by_scenario(free_allocations, scenarios["free_allocations"])
    free_allocations = years_to_rows(free_allocations, year_name="Period",
                                     value_name="Free Allocations")

    return free_allocations


def select_h2share(h2share_raw: pd.DataFrame,
                   projects: pd.DataFrame,
                   auction_year: int = None):

    h2share = choose_by_projects(h2share_raw, projects)
    h2share = years_to_rows(h2share, year_name="Operation Year", value_name="H2 Share")
    h2share = get_h2share_opyear(h2share, projects, auction_year)

    return h2share


def choose_by_scenario_dict(data_all: pd.DataFrame, scenarios: dict):
    return pd.concat([
        data_all
        .query(f"Component=='{component}'")
        .query(f"Scenario=='{scenario}'")
        .drop(columns=["Scenario"])
        for component, scenario in scenarios.items()
    ])


def choose_by_scenario(data_all: pd.DataFrame, scenario: str):
    return data_all \
        .query(f"Scenario=='{scenario}'") \
        .drop(columns=["Scenario"])


def choose_by_projects(h2share: pd.DataFrame, projects: pd.DataFrame):
    return projects \
        .filter(['Project name', 'H2 Share Scenario']) \
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


def get_h2share_opyear(h2share: pd.DataFrame, projects: pd.DataFrame, auction_year: int = None):
    if auction_year:
        h2share = h2share \
            .assign(Period=lambda df: (df['Operation Year'] - 1) + auction_year + 3) \
            .drop(columns=['Operation Year'])
    else:
        h2share = h2share \
            .merge(
                projects.filter(['Project name', 'Time of investment']),
                how='left',
                on=['Project name']
            ) \
            .assign(Period=lambda df: (df['Operation Year'] - 1) + df['Time of investment']) \
            .drop(columns=['Operation Year', 'Time of investment'])

    return h2share
