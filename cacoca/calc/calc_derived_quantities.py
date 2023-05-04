import pandas as pd
import numpy as np
from ..setup.setup import Setup
from ..tools.common_merges import merge_project_dfs


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
    return merge_project_dfs(cost_and_em, pr_size)


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


def calc_payout(cost_and_em: pd.DataFrame, setup: Setup):
    # caution: payout is still yearly.
    payout_yearly = cost_and_em \
        .assign(
            **{"Difference Price": lambda df:
                df["cost_diff"] / -df["Emissions_diff"] - df["Effective CO2 Price"]}
        )
    payout_yearly = payout_yearly \
        .assign(
            **{"Payout": lambda df:
                df["Difference Price"] * -df["Emissions_diff"] * df["Size"]}
        )
    payout_aggregate = payout_yearly \
        .groupby('Project name') \
        .agg({'Payout': 'sum'})
    payout_sum = np.sum(payout_yearly['Payout'].values)
    return payout_yearly, payout_aggregate, payout_sum


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
