import pandas as pd


def calc_ccfd(data_all: pd.DataFrame, projects: pd.DataFrame):

    data_all = data_all \
        .assign(
            **{"Effective CO2 Price": lambda df:
                (df["Emissions_diff"] - df["Free Allocations_diff"])
                / df["Emissions_diff"]
                * df["CO2 Price"]}
        )

    data_all = data_all \
        .assign(
            **{"Difference Price": lambda df:
                df["OPEX_diff"]
                / -df["Emissions_diff"]
                - df["Effective CO2 Price"]}
        )

    data_all = data_all \
        .merge(
            projects
            .rename(columns={'Project size/Production capacity [Mt/a] or GW': 'Size'})
            .filter(['Project name', 'Size']),
            how='left',
            on=['Project name']
        ) \
        .assign(
            **{"Payout": lambda df:
                df["Difference Price"] * -df["Emissions_diff"] * df["Size"]}
        )

    return data_all