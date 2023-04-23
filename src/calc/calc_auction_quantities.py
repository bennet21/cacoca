import pandas as pd
import numpy as np
from src.setup.setup import Setup
from src.setup.select_scenario_data import select_prices
from src.tools.tools import merge_dfs


def calc_auction_quantities(yearly: pd.DataFrame, setup: Setup, auction_config: dict):
    strike_price = calc_strike_price(yearly, setup)
    yearly, cap_aggregate = calc_budget_cap(yearly, strike_price, setup.prices_raw, auction_config)
    rel_em_red = calc_relative_emission_reduction(yearly, auction_config)
    aggregate = merge_dfs(strike_price, cap_aggregate, rel_em_red)
    return yearly, aggregate


def calc_strike_price(yearly: pd.DataFrame, setup: Setup):

    # NPV of cost difference and Emissions savings
    data = yearly \
        .merge(
            setup.projects_current.filter(
                ['Project name', 'WACC', 'Time of investment', 'Project duration [a]']),
            how='left',
            on=['Project name']
        ) \
        .assign(
            **{'CumInterest': lambda df:
               (1. + df['WACC'])**(df['Period'] - df['Time of investment'])}
        ) \
        .assign(
            **{'cost_NPV': lambda df:
               (df['CumInterest'] * df['cost_diff']) / df['Project duration [a]']}
        ) \
        .assign(
            **{'Emissions_NPV': lambda df:
               (df['CumInterest'] * df['Emissions_diff']) / df['Project duration [a]']}
        ) \
        .groupby(['Project name']) \
        .agg({'cost_NPV': 'sum', 'Emissions_NPV': 'sum'})

    # NPV(Cost_diff - SP*Emission_diff) = 0,
    # so  SP = NPV(Cost_diff)/NPV(Emission_diff)
    data = data \
        .assign(
            **{'Strike Price': lambda df:
               -df['cost_NPV'] / df['Emissions_NPV']}
        ) \
        .filter(['Project name', 'Strike Price'])

    return data


def calc_budget_cap(yearly: pd.DataFrame, strike_price: pd.DataFrame, prices_raw: pd.DataFrame,
                    config_ar: dict):
    alpha = config_ar['budget_cap_alpha']
    scendict = {'prices': {'CO2': config_ar['budget_cap_co2_price_scen']}}
    prices_co2 = select_prices(prices_raw, scendict)
    prices_co2 = prices_co2 \
        .rename(columns={'Price': 'min_co2_price'}) \
        .filter(['Period', 'min_co2_price'])

    yearly = yearly \
        .merge(strike_price, how='left', on=['Project name']) \
        .merge(prices_co2, how='left', on=['Period'])

    yearly['delta_k'] = alpha / -yearly['Emissions_diff'] \
        * (yearly['Energy cost'] + yearly['Energy cost_ref'] / (1. + alpha))
    yearly['budget_cap'] \
        = (yearly['Strike Price'] + yearly['delta_k'] - yearly['min_co2_price']) \
        * -yearly['Emissions_diff'] * yearly['Size']

    cap_aggregate = yearly \
        .groupby(['Project name']) \
        .agg({'budget_cap': 'sum'})

    return yearly, cap_aggregate


def calc_relative_emission_reduction(yearly: pd.DataFrame, auction_config: dict):
    auction_year = auction_config['year']
    s = auction_config['rel_em_red_s']
    rr = auction_config['rel_em_red_rr']
    rel_em_red = yearly \
        .query(f"Period >= {auction_year+3} & Period <= {auction_year+7}") \
        .assign(**{'rel_em_red': lambda df: -df['Emissions_diff'] / df['Emissions_ref']}) \
        .groupby(['Project name']) \
        .agg({'rel_em_red': 'mean'})
    rel_em_red['rel_em_red_fr'] = 1. + s * (rel_em_red['rel_em_red'] - rr)
    rel_em_red['rel_em_red_fr'] = np.maximum(np.minimum(rel_em_red['rel_em_red_fr'], 1.2), 0.8)

    return rel_em_red
