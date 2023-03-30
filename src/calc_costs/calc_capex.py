import numpy_financial as npf
import pandas as pd


def calc_capex(projects: pd.DataFrame, techdata: pd.DataFrame):

    def single_tech_param(name: str):
        return techdata.query(f"Type=='{name}'") \
            .filter(["Technology", "Value"]) \
            .rename(columns={"Value": name})

    projects = projects \
        .merge(single_tech_param('High CAPEX'), how='left', on='Technology') \
        .merge(single_tech_param('Low CAPEX'), how='left', on='Technology') \
        .assign(
            **{'CAPEX': lambda df:
                df['Share of high CAPEX'] * df['High CAPEX'].fillna(0.).astype(float)
                + (1. - df['Share of high CAPEX']) * df['Low CAPEX'].fillna(0.).astype(float)}
        )

    projects = projects \
        .assign(
            **{'Invest Volume (M EUR)': lambda df:
                df['CAPEX'] * df['Project size/Production capacity [Mt/a] or GW']}
        ) \
        .assign(
            **{"Allocated CAPEX": lambda df:
                # NB: npf.pmt already divides by lifetime to get cost per t of product
                npf.pmt(df['WACC'], df['Technical lifetime'], -df['CAPEX'])
                * df['Project size/Production capacity [Mt/a] or GW']
                / df['Planned production volume p.a.']}
        )

    return projects
