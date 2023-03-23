import numpy_financial as npf

def calc_capex(projects, techdata):
    def single_tech_param(name: str):
        return techdata.query(f"Type=='{name}'") \
            .filter(["Technology", "Reported value"]) \
            .rename(columns={"Reported value": name})

    projects = projects \
        .merge(single_tech_param('High CAPEX'), how='left', on='Technology') \
        .merge(single_tech_param('Low CAPEX'), how='left', on='Technology') \
        .assign(CAPEX=lambda df:       df['Share of high CAPEX']  * df['High CAPEX'].astype(float) \
                            + (1. - df['Share of high CAPEX']) * df['Low CAPEX'].astype(float)) \
        .assign(Invest_Volume_MEUR=lambda df: df['CAPEX']* df['Project size/Production capacity [Mt/a] or GW']) \
        .assign(Allocated_CAPEX=lambda df: npf.pmt(df['WACC'], df['Technical lifetime'], -df['CAPEX']) \
                * df['Project size/Production capacity [Mt/a] or GW'] / df['Planned production volume p.a.'])
    
    return projects