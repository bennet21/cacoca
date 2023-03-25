import pandas as pd
from src.input.read_scenario_data import ScenarioData


def calc_opex(projects: pd.DataFrame, techdata: pd.DataFrame,
              reference_tech: pd.DataFrame, scendata: ScenarioData,
              h2share: pd.DataFrame, config: dict):

    # Remove all unnecessary columns, then add columns
    # with reference technology and with industry (sector)
    # We use the reference tech for two purposes:
    # to get the reference opex, and to calculate changing fuel mixes.
    opex = projects.filter(['Project name', 'Technology', 'Time of investment']) \
        .merge(
            reference_tech,
            how='left',
            on="Technology"
        ) \
        .merge(
            techdata
            .filter(["Industry", "Technology"])
            .drop_duplicates(),
            how='left',
            on="Technology"
        )
    # used for reference opex
    opex_ref = opex \
        .drop(columns=["Industry", "Technology"]) \
        .rename(columns={"Reference Technology": "Technology"})

    # generate "new" and "old" opex to blend via fuel mix/h2share
    # for steel_dri, the new Technology name gets '-H2' added, while the old
    # Technology is the new (not the Reference!) with -NG added.
    opex.loc[opex['Industry'] == 'steel_dri', 'Technology'] += "-H2"
    opex.loc[opex['Industry'] == 'steel_dri', 'Reference Technology'] \
        = opex.loc[opex['Industry'] == 'steel_dri', 'Technology'] + "-NG"

    opex_old = opex \
        .drop(columns=["Industry", "Technology"]) \
        .rename(columns={"Reference Technology": "Technology"})
    opex_new = opex \
        .drop(columns=["Industry", "Reference Technology"])

    # calc opex for each fuel mix
    opex_old = get_opex_single_opmode(opex_old, config, techdata, scendata)
    opex_new = get_opex_single_opmode(opex_new, config, techdata, scendata)
    opex_ref = get_opex_single_opmode(opex_ref, config, techdata, scendata)

    # blend old and new opex by share of new operation mode
    opex = opex_old \
        .merge(
            opex_new,
            how='left',
            on=['Project name', 'Period']
        ) \
        .merge(
            h2share,
            how='left',
            on=['Project name', 'Period']
        ) \
        .assign(
            OPEX=lambda df: (1.-df['H2 Share']) * df['Cost_x'] + df['H2 Share'] * df['Cost_y']
        ) \
        .drop(columns=['H2 Share', 'Cost_x', 'Cost_y'])

    opex_ref.rename(columns={'Cost': 'OPEX'}, inplace=True)

    return opex, opex_ref


def get_opex_single_opmode(projects_in: pd.DataFrame, config: dict,
                           techdata: pd.DataFrame, scendata: ScenarioData):
    """
    Calc opex for one set of specific eneryg demands
    """

    # get unique list of all occuring components of energy demand
    fuels = techdata \
        .query("Type=='Energy demand'") \
        .filter(["Component"]) \
        .drop_duplicates()

    # expand projects by calendar years of operation
    opex = projects_in.merge(
            pd.DataFrame.from_dict({'Period': config['years']}),
            how='cross'
        ) \
        .query("Period >= `Time of investment` & Period <= `Time of investment` + 15.") \
        .drop(columns=['Time of investment']) \
        .merge(fuels, how='cross')

    # get specific energy demand from techdata, accessed by technology and component
    # This is done after expanding by year to later enable time-dependent eneryg demands
    opex = opex \
        .merge(
            techdata
            .query("Type=='Energy demand'")
            .filter(["Technology", "Component", "Value"]),
            how='left',
            on=['Technology', 'Component']
        ) \
        .rename(columns={"Value": "Energy demand"})
    opex["Energy demand"].fillna(0., inplace=True)

    # add prices to opex df and calculate cost = en.demand * price
    opex = opex \
        .merge(
            scendata.prices.drop(columns=["Source Reference", "Unit"]),
            how='left',
            on=['Component', 'Period']
        ) \
        .assign(Cost=lambda df: df['Energy demand'] * df['Price']) \
        .groupby(['Project name', 'Period'], as_index=False) \
        .agg({'Cost': 'sum'})

    return opex
