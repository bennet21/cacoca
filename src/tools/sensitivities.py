import pandas as pd
import numpy as np
import copy
from src.setup.setup import Setup
from src.tools.common_merges import merge_project_dfs


index_vars = ['Project name', 'Technology', 'Industry', 'Period']


def varnames(df: pd.DataFrame):
    return df.columns.difference(index_vars)


def with_sensitivities(run_func):
    def sensitivity_wrapper(setup: Setup):
        base = run_func(setup)
        variance_sum = init_variance_sum(base)
        stds = setup.config.get('relative_standard_deviation', {})
        for component, std in stds.items():
            setup_dist = copy.copy(setup)
            setup_dist.prices = disturb(setup.prices, component)
            disturbed = run_func(setup_dist)
            std_df = get_yearly_std(setup.prices, component, std)
            variance_sum = sensitivity_to_variance(variance_sum, base, disturbed, std_df)
        base = get_bounds(base, variance_sum)
        return base
    return sensitivity_wrapper


def init_variance_sum(base: pd.DataFrame):
    variance_sum = base.copy()
    variance_sum[varnames(base)] = 0.
    return variance_sum


def sensitivity_to_variance(variance_sum: pd.DataFrame, base: pd.DataFrame, disturbed: pd.DataFrame,
                            std_df: pd.DataFrame):
    vns = varnames(base)
    df_all = merge_project_dfs(base, disturbed) \
        .merge(std_df, how='left', on='Period')
    for vn in vns:
        variance_sum[vn] += ((df_all[vn + '_y'] - df_all[vn + '_x']) * df_all['StD']) ** 2
    return variance_sum


def get_yearly_std(prices: pd.DataFrame, component: str, rel_std: float):
    # transform relative or absolute std to yearly data frame
    rows = prices["Component"] == component
    std_df = prices.loc[rows, ['Period', 'Price']].copy()
    std_df['StD'] = std_df['Price'] * rel_std
    return std_df.filter(['Period', 'StD'])


def get_bounds(base: pd.DataFrame, variance: pd.DataFrame):
    for vname in varnames(base):
        if np.max(variance[vname].values) > 1.e-10:
            base[vname + '_lower'] = base[vname] - 2. * np.sqrt(variance[vname])
            base[vname + '_upper'] = base[vname] + 2. * np.sqrt(variance[vname])
    return base


def disturb(prices: pd.DataFrame, component: str):
    rows = prices["Component"] == component
    prices_out = prices.copy()
    prices_out.loc[rows, 'Price'] = prices_out.loc[rows, 'Price'] + 1
    return prices_out
