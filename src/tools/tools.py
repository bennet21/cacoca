import pandas as pd


def log(s: str):
    print(s)


def merge_dfs(*dfs: pd.DataFrame):
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
