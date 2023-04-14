import pandas as pd
import numpy as np


variance_suffix = '_variance'


def add(df: pd.DataFrame, v1: str, v2: str):
    """
    Returns expectation and variance of v1 + v2.
    Input can either be a column name string, or a constant to multiply with, or a tuple of mean
    and variance.
    According variance column name is searched for automatically in df, and used if present.
    """
    exp1, var1 = split_exp_and_var(df, v1)
    exp2, var2 = split_exp_and_var(df, v2)
    exp = exp1 + exp2
    var = var1 + var2
    return exp, var


def sub(df: pd.DataFrame, v1: str, v2: str):
    """
    Returns expectation and variance of v1 - v2.
    Input can either be a column name string, or a constant to multiply with, or a tuple of mean
    and variance.
    According variance column name is searched for automatically in df, and used if present.
    """
    exp1, var1 = split_exp_and_var(df, v1)
    exp2, var2 = split_exp_and_var(df, v2)
    exp = exp1 - exp2
    var = var1 + var2
    return exp, var


def mul(df: pd.DataFrame, v1: str, v2: str):
    """
    Returns expectation and variance of v1 * v2.
    Input can either be a column name string, or a constant to multiply with, or a tuple of mean
    and variance.
    According variance column name is searched for automatically in df, and used if present.
    """
    exp1, var1 = split_exp_and_var(df, v1)
    exp2, var2 = split_exp_and_var(df, v2)
    exp = exp1 * exp2
    var = (exp1**2 + var1) * (exp2**2 + var2) - exp1**2 * exp2**2
    return exp, var


def div(df: pd.DataFrame, v1: str, v2: str):
    """
    Returns expectation and variance of v1 / v2.
    Input can either be a column name string, or a constant to multiply with, or a tuple of mean
    and variance.
    According variance column name is searched for automatically in df, and used if present.
    """
    exp1, var1 = split_exp_and_var(df, v1)
    exp2, var2 = split_exp_and_var(df, v2)
    if var2 != 0.:
        raise Exception(f'Cannot divide by random variable ({v2})!')
    exp = exp1 / exp2
    var = var1 / exp2**2
    return exp, var


def minus(df: pd.DataFrame, v: str):
    """
    Returns expectation and variance of -v.
    Input can either be a column name string, or a constant to multiply with, or a tuple of mean
    and variance.
    According variance column name is searched for automatically in df, and used if present.
    """
    return mul(df, v, -1.)


def split_exp_and_var(df: pd.DataFrame, v: str):
    if isinstance(v, str):
        exp = df[v]
        var = df[v + variance_suffix] if v + variance_suffix in df.columns else 0.
    elif isinstance(v, tuple):
        exp, var = v
    else:
        exp, var = v, 0.
    return exp, var


def exp(f):
    def exp_wrapper(df):
        out = f(df)
        return out[0]
    return exp_wrapper


def var(f):
    def var_wrapper(df):
        out = f(df)
        return out[1]
    return var_wrapper


def dict(name, f):
    return {name: exp(f), name + variance_suffix: var(f)}


def get_bounds(df_in: pd.DataFrame):
    for vname in df_in.columns:
        vns = vname + variance_suffix
        if vns in df_in.columns:
            assign_dict = {
                vname + '_lower': lambda df: df[vname] - 2. * np.sqrt(df[vns]),
                vname + '_upper': lambda df: df[vname] + 2. * np.sqrt(df[vns])}
            df_in = df_in.assign(**assign_dict)
    return df_in


def add_variance(prices: pd.DataFrame,
                 relative_standard_deviation: dict = None,
                 absolute_standard_deviation: dict = None):

    # prices.insert(loc=len(prices.columns),
    #               column='Price_variance', value=0.)
    if relative_standard_deviation:
        for component, factor in relative_standard_deviation.items():
            h2rows = prices["Component"] == component
            prices.loc[h2rows, 'Price_variance'] \
                = (factor * prices.loc[h2rows, 'Price'])**2

    if absolute_standard_deviation:
        for component, std in absolute_standard_deviation.items():
            h2rows = prices["Component"] == component
            prices.loc[h2rows, 'Price_variance'] = std**2
