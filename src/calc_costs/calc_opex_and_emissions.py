import pandas as pd
from src.input.read_scenario_data import ScenarioData


def calc_opex_and_emissions(projects: pd.DataFrame, techdata: pd.DataFrame,
                            reference_tech: pd.DataFrame, scendata: ScenarioData,
                            h2share: pd.DataFrame, config: dict):

    data_old, data_new, data_ref = split_technology_names(projects, techdata, reference_tech)

    data_new = calc_single_opmode(data_new, config, techdata, scendata)
    data_old = calc_single_opmode(data_old, config, techdata, scendata)
    data_ref = calc_single_opmode(data_ref, config, techdata, scendata)

    data_all = merge_operation_modes(data_old, data_new, h2share,
                                     variables=['OPEX', 'Emissions', 'Free Allocations'])

    data_all = merge_with_reference(data_all, data_ref,
                                    variables=['OPEX', 'Emissions', 'Free Allocations'])

    return data_all


def split_technology_names(projects: pd.DataFrame, techdata: pd.DataFrame,
                           reference_tech: pd.DataFrame):

    industries = techdata \
        .filter(["Technology", "Industry"]) \
        .drop_duplicates()

    data_all = projects.filter(['Project name', 'Technology', 'Time of investment']) \
        .merge(
            reference_tech,
            how='left',
            on="Technology"
        ) \
        .merge(
            industries,
            how='left',
            on="Technology"
        )

    # used for reference opex
    data_ref = data_all \
        .drop(columns=["Industry", "Technology"]) \
        .rename(columns={"Reference Technology": "Technology"})

    # generate "new" and "old" opex to blend via fuel mix/h2share
    # for steel_dri, the new Technology name gets '-H2' added, while the old
    # Technology is the new (not the Reference!) with -NG added.
    data_all.loc[data_all['Industry'] == 'steel_dri', 'Reference Technology'] \
        = data_all.loc[data_all['Industry'] == 'steel_dri', 'Technology'] + "-NG"
    data_all.loc[data_all['Industry'] == 'steel_dri', 'Technology'] += "-H2"

    data_old = data_all \
        .drop(columns=["Industry", "Technology"]) \
        .rename(columns={"Reference Technology": "Technology"})
    data_new = data_all \
        .drop(columns=["Industry", "Reference Technology"])

    return data_old, data_new, data_ref


def calc_single_opmode(projects_in: pd.DataFrame, config: dict,
                       techdata: pd.DataFrame, scendata: ScenarioData):
    """
    Calc opex and emissions for one set of specific energy demands
    """

    # expand projects by calendar years of operation
    yearly_data = projects_in.merge(
            pd.DataFrame.from_dict({'Period': config['years']}),
            how='cross'
        ) \
        .query("Period >= `Time of investment` & Period <= `Time of investment` + 15.") \
        .drop(columns=['Time of investment'])

    yearly_data = calc_opex_single_opmode(yearly_data, techdata, scendata)

    yearly_data = calc_emissions_single_opmode(yearly_data, techdata, scendata)

    return yearly_data


def calc_opex_single_opmode(yearly_data: pd.DataFrame, techdata: pd.DataFrame,
                            scendata: ScenarioData):
    """
    Calc opex for one set of specific energy demands
    """

    # expand by unique list of all occuring components of energy demand
    materials_in = techdata \
        .query("Type=='Energy demand' | Type=='Feedstock demand'") \
        .filter(["Component"]) \
        .drop_duplicates()
    yearly_data = yearly_data.merge(materials_in, how='cross')

    # get specific energy demand from techdata, accessed by technology and component
    # This is done after expanding by year to later enable time-dependent eneryg demands
    yearly_data = yearly_data \
        .merge(
            techdata
            .query("Type=='Energy demand' | Type=='Feedstock demand'")
            .filter(["Technology", "Component", "Value"]),
            how='left',
            on=['Technology', 'Component']
        ) \
        .rename(columns={"Value": "Material demand"})
    yearly_data["Material demand"].fillna(0., inplace=True)

    # add prices to opex df and calculate OPEX = en.demand * price
    yearly_data = yearly_data \
        .merge(
            scendata.prices.drop(columns=["Source Reference", "Unit"]),
            how='left',
            on=['Component', 'Period']
        ) \
        .assign(OPEX=lambda df: df['Material demand'] * df['Price']) \
        .groupby(['Project name', 'Period'], as_index=False) \
        .agg({'OPEX': 'sum', 'Technology': 'first'})

    # add additional OPEX
    yearly_data = yearly_data \
        .merge(
            techdata
            .query("Type=='OPEX'")
            .filter(["Technology", "Value"]),
            how='left',
            on=['Technology']
        ) \
        .rename(columns={"Value": "Additional OPEX"})
    yearly_data["Additional OPEX"].fillna(0., inplace=True)
    yearly_data = yearly_data \
        .assign(OPEX=lambda df: df['OPEX'] + df['Additional OPEX']) \
        .drop(columns=['Additional OPEX'])

    return yearly_data


def calc_emissions_single_opmode(yearly_data: pd.DataFrame, techdata: pd.DataFrame,
                                 scendata: ScenarioData):
    """
    Calc emission prices for one set of specific energy demands
    """

    # Add emissions to df
    yearly_data = yearly_data \
        .merge(
            techdata
            .query("Type=='Emissions' & Component == 'CO2'")
            .filter(["Technology", "Value"]),
            how='left',
            on=['Technology']
        ) \
        .rename(columns={"Value": "Emissions"})

    # Add CO2 price to df
    co2prices = scendata.prices \
        .query("Component == 'CO2'") \
        .filter(["Period", "Price"]) \
        .rename(columns={"Price": "CO2 Price"})
    yearly_data = yearly_data \
        .merge(
            co2prices,
            how='left',
            on=['Period']
        ) \

    # add free allocations to df
    yearly_data = yearly_data \
        .merge(
            scendata.free_allocations
            .filter(["Technology", "Period", "Free Allocations"]),
            how='left',
            on=['Technology', 'Period']
        )
    yearly_data["Free Allocations"].fillna(0., inplace=True)

    return yearly_data


def merge_operation_modes(data_old: pd.DataFrame, data_new: pd.DataFrame,
                          h2share: pd.DataFrame, variables: list):
    # merge old and new dataframes
    data_all = data_old \
        .merge(
            data_new,
            how='left',
            on=['Project name', 'Period']
        ) \
        .merge(
            h2share,
            how='left',
            on=['Project name', 'Period']
        )

    # blend opex and emissions of old and new operation mode to overall opex
    for vname in variables:
        data_all = data_all \
            .assign(
                **{vname: lambda df:
                    (1.-df['H2 Share']) * df[vname+'_x'] + df['H2 Share'] * df[vname+'_y']
                   }
            ) \
            .drop(columns=[vname+suffix for suffix in ['_x', '_y']])

    data_all = data_all \
        .drop(columns=['H2 Share', 'Technology_x']) \
        .rename(columns={'Technology_y': 'Technology'})

    return data_all


def merge_with_reference(data_all: pd.DataFrame, data_ref: pd.DataFrame, variables: list):

    # add '_ref' to reference varable names
    data_ref = data_ref \
        .rename(
            columns={v: v + '_ref' for v in variables}
        ) \
        .drop(columns=['Technology'])
    # merge and calculate difference for all variables in input list
    data_all = data_all \
        .merge(
            data_ref,
            how='left',
            on=['Project name', 'Period']
        )
    for vname in variables:
        data_all = data_all \
            .assign(
                **{vname + '_diff': lambda df: df[vname] - df[vname + '_ref']}
            )

    return data_all
