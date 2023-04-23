import pandas as pd
from src.setup.setup import Setup
from src.tools.tools import merge_dfs


def calc_derived_quantities(cost_and_em: pd.DataFrame, setup: Setup):
    yearly = add_size(cost_and_em, setup)
    yearly = add_effective_co2_price(yearly)
    yearly = add_abatement_cost(yearly, setup)
    return yearly


def add_size(cost_and_em: pd.DataFrame, setup: Setup):
    pr_size = setup.projects_current \
        .rename(columns={
            'Planned production volume p.a.': 'Size'
        }) \
        .filter(['Project name', 'Size'])
    return merge_dfs(cost_and_em, pr_size)


def add_effective_co2_price(cost_and_em: pd.DataFrame):
    cost_and_em = cost_and_em \
        .assign(**{"Effective CO2 Price": lambda df:
                   df["CO2 Price"] *
                   (df["Emissions_diff"] - df["Free Allocations_diff"]) / df["Emissions_diff"]})
    return cost_and_em


def add_abatement_cost(cost_and_em: pd.DataFrame, setup: Setup):
    cost_and_em = cost_and_em \
        .merge(
            setup.techdata.filter(['Technology', 'Industry']).drop_duplicates(),
            how='left',
            on=['Technology']
        ) \
        .assign(**{'Abatement_cost': lambda df: df["cost_diff"] / -df['Emissions_diff']})
    return cost_and_em


# total_em_savings = cost_and_em \
#     .groupby(['Project name']) \
#     .agg({'Emissions_diff': 'sum'}) \
#     .merge(
#         pr_size,
#         how='left',
#         on=['Project name']
#     ) \
#     .assign(
#         **{"Total Emissions savings": lambda df:
#             df["Emissions_diff"] * df['Size']}
#     ) \
#     .filter(['Project name', "Total Emissions savings"])

# cost_and_em = cost_and_em \
#     .assign(
#         **{"Difference Price": lambda df:
#             (df["cost_diff"] / -df["Emissions_diff"]) -
#             df["Effective CO2 Price"]}
#     )

# cost_and_em = cost_and_em \
#     .merge(
#         pr_size,
#         how='left',
#         on=['Project name']
#     ) \
#     .assign(
#         **{"Payout": lambda df:
#             df["Difference Price"] * -df["Emissions_diff"] * df["Size"]}
#     )
