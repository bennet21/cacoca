import pandas as pd
from src.setup.select_scenario_data import select_prices


def calc_strike_price(cost_and_em: pd.DataFrame, projects: pd.DataFrame):

    # NPV of cost difference and Emissions savings
    data = cost_and_em \
        .merge(
            projects.filter(['Project name', 'WACC', 'Time of investment', 'Project duration [a]']),
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


def calc_ccfd(cost_and_em: pd.DataFrame, projects: pd.DataFrame, techdata: pd.DataFrame):

    pr_size = projects \
        .rename(columns={
            'Planned production volume p.a.': 'Size'
            # 'Project size/Production capacity [Mt/a] or GW': 'Size'
        }) \
        .filter(['Project name', 'Size'])

    cost_and_em = cost_and_em \
        .assign(**{"Effective CO2 Price": lambda df:
                   df["CO2 Price"] *
                   (df["Emissions_diff"] - df["Free Allocations_diff"]) / df["Emissions_diff"]})

    cost_and_em = cost_and_em \
        .merge(
            techdata.filter(['Technology', 'Industry']),
            how='left',
            on=['Technology']
        ) \
        .assign(**{'Abatement_cost': lambda df: df["cost_diff"] / -df['Emissions_diff']})

    total_em_savings = cost_and_em \
        .groupby(['Project name']) \
        .agg({'Emissions_diff': 'sum'}) \
        .merge(
            pr_size,
            how='left',
            on=['Project name']
        ) \
        .assign(
            **{"Total Emissions savings": lambda df:
                df["Emissions_diff"] * df['Size']}
        ) \
        .filter(['Project name', "Total Emissions savings"])

    cost_and_em = cost_and_em \
        .assign(
            **{"Difference Price": lambda df:
                (df["cost_diff"] / -df["Emissions_diff"]) -
                df["Effective CO2 Price"]}
        )

    cost_and_em = cost_and_em \
        .merge(
            pr_size,
            how='left',
            on=['Project name']
        ) \
        .assign(
            **{"Payout": lambda df:
                df["Difference Price"] * -df["Emissions_diff"] * df["Size"]}
        )

    return cost_and_em, total_em_savings


def calc_budget_cap(cost_and_em: pd.DataFrame, strike_price: pd.DataFrame, prices_raw: pd.DataFrame,
                    config_ar: dict):
    alpha = config_ar['budget_cap_alpha']
    scendict = {'prices': {'CO2': config_ar['budget_cap_co2_price_scen']}}
    prices_co2 = select_prices(prices_raw, scendict)
    prices_co2 = prices_co2 \
        .rename(columns={'Price': 'min_co2_price'}) \
        .filter(['Period', 'min_co2_price'])

    cost_and_em = cost_and_em \
        .merge(strike_price, how='left', on=['Project name']) \
        .merge(prices_co2, how='left', on=['Period'])

    cost_and_em['delta_k'] = alpha / cost_and_em['Emissions_diff'] \
        * (cost_and_em['Energy cost'] + cost_and_em['Energy cost_ref'] / (1. + alpha))
    cost_and_em['budget_cap'] \
        = (cost_and_em['Strike Price'] + cost_and_em['delta_k'] - cost_and_em['min_co2_price']) \
        * cost_and_em['Emissions_diff'] * cost_and_em['Size']

    cap_aggregate = cost_and_em \
        .groupby(['Project name']) \
        .agg({'budget_cap': 'sum'})

    return cost_and_em, cap_aggregate


def calc_relative_emission_reduction(cost_and_em: pd.DataFrame, auction_config: dict):
    auction_year = auction_config['year']
    s = auction_config['rel_em_red_s']
    rr = auction_config['rel_em_red_rr']
    rel_em_red = cost_and_em \
        .query(f"Period >= {auction_year+3} & Period <= {auction_year+7}") \
        .assign(**{'rel_em_red': lambda df: -df['Emissions_diff'] / df['Emissions_ref']}) \
        .groupby(['Project name']) \
        .agg({'rel_em_red': 'mean'})
    rel_em_red['rel_em_red_fr'] = 1. + s * (rel_em_red['rel_em_red'] - rr)
    return rel_em_red
