import pandas as pd
from ..setup.setup import Setup


def merge_project_dfs(*dfs: pd.DataFrame):
    # if one df has 'Period' column, use that as 'left' (else the first)
    df_lhs = next((df for df in dfs if 'Period' in df.columns), dfs[0])
    df_out = df_lhs.copy()
    for df_rhs in dfs:
        if df_lhs is df_rhs:
            continue
        elif 'Period' in df_rhs.columns:
            df_out = df_out.merge(df_rhs, how='left', on=['Project name', 'Period'])
        else:
            df_out = df_out.merge(df_rhs, how='left', on=['Project name'])
    return df_out


def add_tech_and_industry(project_df: pd.DataFrame, setup: Setup):
    if 'Technology' not in project_df.columns:
        project_df = project_df \
            .merge(
                setup.projects_current.filter(['Project name', 'Technology']),
                how='left',
                on='Project name'
            )

    industries = setup.techdata \
        .filter(["Technology", "Industry"]) \
        .drop_duplicates()

    project_df = project_df \
        .merge(
            industries,
            how='left',
            on="Technology"
        )
    return project_df
