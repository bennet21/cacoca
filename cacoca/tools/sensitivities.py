import pandas as pd
import numpy as np
import copy
from ..setup.setup import Setup
from ..setup.select_scenario_data import choose_by_scenario, years_to_rows
from .common_merges import merge_project_dfs


# format in config:

# uncertain_parameters:
# - is_relative: True
#   std_value: 0.1
#   std_scenario: 'MyScenarioName'
#   data_frame: 'prices'
#   filters:
#     Component: 'CO2'


index_vars = ['Project name', 'Technology', 'Industry', 'Period']


def var_names(df: pd.DataFrame):
    return df.columns.difference(index_vars)


def with_sensitivities(run_func):
    def sensitivity_wrapper(setup: Setup):
        output_base = run_func(setup)
        variance_sum = init_variance_sum(output_base)
        cfg_dicts = setup.config.get('uncertain_parameters', [])
        for cfg_uct_prm in cfg_dicts:
            setup_disturbed = copy.copy(setup)
            disturb_input(setup_disturbed, cfg_uct_prm)
            output_disturbed = run_func(setup_disturbed)
            variance_sum = sensitivity_to_variance(variance_sum, output_base, output_disturbed)
        output_base = get_bounds(output_base, variance_sum)
        return output_base
    return sensitivity_wrapper


def init_variance_sum(base: pd.DataFrame):
    variance_sum = base.copy()
    variance_sum[var_names(base)] = 0.
    return sort_df(variance_sum)


def sort_df(df: pd.DataFrame):
    cols = ['Project name', 'Period'] if 'Period' in df.columns else ['Project name']
    return df.sort_values(cols)


def sensitivity_to_variance(variance_sum: pd.DataFrame, output_base: pd.DataFrame,
                            output_disturbed: pd.DataFrame):
    vns = var_names(output_base)
    df_all = merge_project_dfs(output_base, output_disturbed)
    df_all = sort_df(df_all)
    for vn in vns:
        variance_sum[vn] += (df_all[vn + '_y'] - df_all[vn + '_x']) ** 2
    return variance_sum


def select_std_scenario(setup: Setup, std_scenario: float):
    std_df = choose_by_scenario(setup.abs_std_raw, std_scenario)
    std_df = years_to_rows(std_df, year_name="Period", value_name="StD")
    return std_df.filter(['Period', 'StD']).fillna(0.)


def get_bounds(base: pd.DataFrame, variance: pd.DataFrame):
    variance = variance.sort_values(['Project name', 'Period'])
    base = base.sort_values(['Project name', 'Period'])
    for vname in var_names(base):
        if np.max(variance[vname].values) > 1.e-10:
            base[vname + '_lower'] = base[vname] - 2. * np.sqrt(variance[vname])
            base[vname + '_upper'] = base[vname] + 2. * np.sqrt(variance[vname])
    return base


def disturb_input(setup_disturbed: Setup, cfg_uct_prm: dict):
    # get disturbed df
    if cfg_uct_prm['data_frame'] == 'prices':
        disturb_prices(setup_disturbed, cfg_uct_prm)
    elif cfg_uct_prm['data_frame'] == 'techdata':
        disturb_techdata(setup_disturbed, cfg_uct_prm)
    else:
        raise KeyError('Invalid data_frame name in uncertainties config')


def disturb_prices(setup_disturbed: Setup, cfg_uct_prm: dict):

    if 'std_scenario' in cfg_uct_prm == 'std_value' in cfg_uct_prm:
        raise KeyError("Please specify 'std_scenario' xor 'std_value' for each price uncertainty")

    prices = setup_disturbed.prices.copy()
    rows = get_rows_by_filters(prices, cfg_uct_prm['filters'])

    prices_filtered = prices.loc[rows, ['Period', 'Price']]
    if 'std_scenario' in cfg_uct_prm:
        std_scen = select_std_scenario(setup_disturbed, cfg_uct_prm['std_scenario'])
        std = prices_filtered.merge(std_scen, on='Period', how='left') \
            .set_index(prices_filtered.index)['StD']
    else:
        std = pd.Series(cfg_uct_prm['std_value'], index=prices_filtered.index, name='StD')

    if cfg_uct_prm['is_relative']:
        std *= prices_filtered['Price']

    prices.loc[rows, 'Price'] = prices.loc[rows, 'Price'] + std
    setup_disturbed.prices = prices


def disturb_techdata(setup_disturbed: Setup, cfg_uct_prm: dict):

    if 'std_value' not in cfg_uct_prm:
        raise KeyError("Please specify 'std_value' for each techdata uncertainty")

    techdata = setup_disturbed.techdata.copy()
    rows = get_rows_by_filters(techdata, cfg_uct_prm['filters'])

    techdata_filtered = techdata.loc[rows, 'Value']
    std = pd.Series(cfg_uct_prm['std_value'], index=techdata_filtered.index, name='StD')

    if cfg_uct_prm['is_relative']:
        std *= techdata_filtered

    techdata.loc[rows, 'Value'] = techdata.loc[rows, 'Value'] + std
    setup_disturbed.techdata = techdata


def get_rows_by_filters(df: pd.DataFrame, filters: dict):
    rows = pd.Series(True, index=df.index, name='rows')
    for column_name, value in filters.items():
        rows_loc = df[column_name] == value
        rows = rows & rows_loc.rename('rows')
    return rows
