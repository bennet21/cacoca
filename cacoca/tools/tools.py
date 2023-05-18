import pandas as pd


def log(s: str):
    print(s)


def filter_df(projects: pd.DataFrame, filter_by: dict):
    for filter_column, filter_values in filter_by.items():
        query_str = " | ".join([f"`{filter_column}` == '{fv}'" for fv in filter_values])
        projects = projects.query(query_str)
    return projects