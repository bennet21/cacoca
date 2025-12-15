import pandas as pd
import numpy_financial as npf


def log(s: str):
    print(s)


def filter_df(projects: pd.DataFrame, filter_by: dict):
    for filter_column, filter_values in filter_by.items():
        query_str = " | ".join([f"`{filter_column}` == '{fv}'" for fv in filter_values])
        projects = projects.query(query_str)
    return projects


def calc_annualized_specific_cost(df: pd.DataFrame, value_col: pd.Series, annuitize: bool = True) -> pd.Series:
    """
    Calculates specific cost (per unit of product) from a capacity-based value.
    Optionally annuitizes the value (using WACC and lifetime) before converting.

    Formula: (Annuity of Value) * Capacity / Production Volume
    """
    if annuitize:
        annual_value = npf.pmt(df['WACC'], df['Technical lifetime'], -value_col)
    else:
        annual_value = value_col

    return (
        annual_value
        * df['Project size/Production capacity [Mt/a] or GW']
        / df['Planned production volume p.a.']
    )