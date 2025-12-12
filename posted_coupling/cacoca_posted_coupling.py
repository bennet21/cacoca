"""Convert Posted technology datasets into CaCoCa-compatible CSV inputs.

This module contains functions to convert technology datasets from the Posted
format into CSV files that are compatible with CaCoCa. The conversion includes translating variable
names, aggregating data, and filtering out unnecessary information. The end
result is a set of CSV files that can be directly used as input for CaCoCa
modeling.

Components can be re-defined via component_type_overrides.
Example component_type_overrides = {"Natural Gas": "Feedstock demand", "Hydrogen": "Feedstock demand"}

TODO:
    - heat emission factor
    - handle CAPEX annualized
    - add low capex
    - get emissions via emissions factor
    - sort by Technology
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Union

from posted.noslag import DataSet

# Components can be re-defined via component_type_overrides.
# Example component_type_overrides = {"Natural Gas": "Feedstock demand", "Hydrogen": "Feedstock demand"}
ENERGY_TYPES = [
    "Electricity",
    "Coal",
    "Natural Gas",
    "Heat",
    "Hydrogen"
]
FEEDSTOCK_TYPES = [
    "Oxygen", 
    "Iron Ore",
    "Scrap Steel",
    "Water",
    "Ammonia",
    "Captured CO2",
    "Steel Slab",
    "Steel Liquid",
    "Cooling Water",
    "Methanol",               
    "Alloys",
    "Directly Reduced Iron",
    "Graphite Electrode",
    "Lime",
    "Nitrogen",
    "Steel Scrap"
]
EMISSION_TYPES = ["CO2"]
# Types that are allowed in the final CaCoCa csv 
ALLOWED_TYPES = {
    "High CAPEX",
    "Low CAPEX",
    "Energy demand",
    "Feedstock demand",
    "OPEX",
    "Emissions",
}
# Types/components that are expected to be removed during filtering
EXPECTED_REMOVAL_TYPES = {
        # specified in project description
        "Lifetime",
        "OCF",
        "Output Capacity",
        "Output", # TODO remove also Output|...
        "Total Output Capacity",

        "Capture Rate", # already in tech name
        # "Total Input Capacity", # TODO what do do with this?
        # "Storage Capacity", # TODO what do do with this?
        # "Total Production Expenditure", # TODO what do do with this?
        # "CAPEX Annualised", # TODO what do do with this?
    }
POSTED_OPEX_COMPONENTS = ['OPEX Variable', 'OPEX Fixed']
ALLOWED_COMPONENTS = [
    "CAPEX",
    "Additional OPEX",
]
TRANSLATION = {"Fossil Gas": "Natural Gas"}
EXCLUDED_TECHNAMES = [
    "Methanol Synthesis with Reforming", # POSTED issue: uses LVH/a unit that Posted does not know
    "Naphtha Steam Cracking", # POSTED issue: kilogram / second' ([mass] / [time]) to 'metric_tonne" failed
    "NGL to Olefins", # POSTED issue: concatenation fails
]

def generate_cacoca_input(target_folder: Path, posted_technames: Union[str, list] = None, posted_datafolder: Path = None, component_type_overrides: Optional[Dict[str, str]] = None):
    """
    Generate CaCoCa-ready CSV files from Posted datasets.

    Parameters
    ----------
    target_folder : Path
        Destination directory for the generated CSV files; created automatically when absent.
    posted_technames : Union[str, list], optional
        One or multiple Posted technology identifiers to process directly. Mutually exclusive with `posted_datafolder`.
    posted_datafolder : Path, optional
        Path containing Posted CSV exports; all detected technologies (except those in `EXCLUDED_TECHNAMES`) are processed.
    component_type_overrides : dict[str, str], optional
        Mapping from component names (e.g. "Natural Gas") to CaCoCa input types ("Energy demand" or "Feedstock demand").
        Overrides affect only variables under the "Input" category and validate supplied labels.

    Raises
    ------
    ValueError
        If neither `posted_technames` nor `posted_datafolder` is provided, if the data folder contains no technologies,
        or if an override supplies an unsupported type label.

    Examples
    --------
    Process all technologies in a folder::

        generate_cacoca_input(Path("out"), posted_datafolder=Path("posted_exports"))

    Override the classification for hydrogen and natural gas while processing selected technologies::

        generate_cacoca_input(
            Path("out"),
            posted_technames=["SMR with CCS", "Hydrogen Electrolysis"],
            component_type_overrides={"Hydrogen": "Feedstock demand", "Natural Gas": "Feedstock demand"},
        )
    """
    # determine technames to process
    if posted_technames is not None:
        technames = posted_technames if isinstance(posted_technames, list) else [posted_technames]
    elif posted_datafolder is not None:
        technames = find_posted_technames(posted_datafolder)
        if not technames:
            raise ValueError(f"No Posted technology files found in folder: {posted_datafolder}")
        technames = [name for name in technames if name not in EXCLUDED_TECHNAMES]
    else:
        raise ValueError("Either posted_datafolder or posted_technames must be provided.")
    
    for techname in technames:
        print(f"Processing Posted technology file: {techname}")
        df_posted, posted_parent_variable = get_posted_df(techname)
        df_cacoca = translate_posted_df_to_cacoca_df(df_posted, posted_parent_variable, component_type_overrides)
        save_cacoca_dataframe(df_cacoca, target_folder, techname)

def find_posted_technames(posted_datafolder: Path):
    """Return the Posted technology names discovered in the given folder."""
    return [f.stem for f in posted_datafolder.glob("*.csv")]

def get_posted_df(posted_techname):
    """Load and aggregate a Posted dataset for the requested technology."""
    posted_parent_variable = f"Tech|{posted_techname}"
    teds = DataSet(posted_parent_variable)
    df_posted = teds.aggregate(region="World", period=2025) 
    df_posted.drop(columns=["region"], inplace=True) # region is redundant
    return df_posted, posted_parent_variable

def translate_posted_df_to_cacoca_df(df_posted: pd.DataFrame, posted_parent_variable: str, component_type_overrides: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Perform end-to-end translation from a Posted dataframe to the CaCoCa schema."""
    df_cacoca = initiate_cacoca_dataframe(df_posted, posted_parent_variable, component_type_overrides)
    df_cacoca = aggregate_opex(df_cacoca)
    df_cacoca = filter_cacoca_dataframe(df_cacoca)
    return df_cacoca

def initiate_cacoca_dataframe(df_posted: pd.DataFrame, posted_parent_variable: str, component_type_overrides: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """Initialize the CaCoCa dataframe with translated metadata and raw values."""
    variable_extraction = df_posted["variable"].apply(lambda v: variable_translation(v, posted_parent_variable, component_type_overrides))
    type_list = [d["Type"] for d in variable_extraction]
    component_list = [d["Component"] for d in variable_extraction]

    tech = df_posted["subtech"] if "subtech" in df_posted.columns else posted_parent_variable.split("|")[-1]
    # if additional differentiation exists, it is added to technology
    used_columns = ["subtech", "variable", "mode", "period", "value", "unit"]
    unused_columns = [col for col in df_posted.columns if col not in used_columns]
    if unused_columns:
        for col in unused_columns:
            tech += "|" + df_posted[col].astype(str)

    # translate Posted columns to CaCoCa columns
    df_cacoca = pd.DataFrame({
        "Technology": tech,
        "Mode": df_posted["mode"] if "mode" in df_posted.columns else None,
        "Type": type_list,
        "Component": component_list,
        "Subcomponent": None,
        "Region": None,
        "Period": df_posted["period"],
        "Usage": None,
        "Value": df_posted["value"],
        "Uncertainty": None,
        "Unit": df_posted["unit"],
        "Non-unit conversion factor": None,
        "Value and uncertainty comment": None,
        "Source reference": f"Posted {posted_parent_variable}",
        "Source comment": None,
    })

    return df_cacoca

def variable_translation(variable: str, parent_variable: str, component_type_overrides: Optional[Dict[str, str]] = None):
    """Translate a Posted variable string into CaCoCa type and component labels."""

    # remove parent variable prefix
    variable = variable.replace(f"{parent_variable}|", "")

    # split variable by "|"
    if "|" in variable:
        type_, component = variable.split("|", 1)
    else:
        type_ = variable
        component = variable

    component = TRANSLATION.get(component, component)

    if type_ == "CAPEX":
        type_ = "High CAPEX"

    elif type_ in POSTED_OPEX_COMPONENTS:
        component = type_ # variable and fixed opex will later be combined to additional opex
        type_ = "OPEX"
    
    elif type_ ==  "Input":
        overrides = component_type_overrides or {}
        override_type = overrides.get(component)
        if override_type:
            if override_type not in {"Energy demand", "Feedstock demand"}:
                raise ValueError(f"Unsupported override '{override_type}' for component '{component}'.")
            type_ = override_type
        elif component in ENERGY_TYPES:
            type_ = "Energy demand"
        elif component in FEEDSTOCK_TYPES:
            type_ = "Feedstock demand"
    
    return {"Type": type_, "Component": component}
            
def aggregate_opex(df_cacoca: pd.DataFrame) -> pd.DataFrame:
    """Sum variable and fixed OPEX components once unit consistency is confirmed."""
    # Ensure OPEX components share compatible units before aggregation.
    is_opex_mask = df_cacoca['Component'].isin(POSTED_OPEX_COMPONENTS)
    df_opex = df_cacoca[is_opex_mask].copy()
    df_other = df_cacoca[~is_opex_mask]

    if not df_opex.empty:
        # sort (as OPEX Variable should be the master for other columns): 
        df_opex['Component'] = pd.Categorical(df_opex['Component'], categories=POSTED_OPEX_COMPONENTS, ordered=True)
        df_opex = df_opex.sort_values("Component")

        # ensure OPEX components share the same unit before aggregation
        grouping_cols = [col for col in df_cacoca.columns if col not in ['Component', 'Value', 'Unit']]
        inconsistent_units = df_opex.groupby(grouping_cols, dropna=False)['Unit'].nunique()
        inconsistent_units = inconsistent_units[inconsistent_units > 1]
        if not inconsistent_units.empty:
            conflicts = []
            for idx in inconsistent_units.index:
                if not grouping_cols:
                    conflicts.append("global")
                else:
                    idx = idx if isinstance(idx, tuple) else (idx,)
                    conflicts.append(", ".join(f"{col}={val}" for col, val in zip(grouping_cols, idx)))
            raise ValueError("OPEX components have incompatible units for: " + "; ".join(conflicts))
        agg_logic = {'Value': 'sum', 'Unit': 'first'}
        aggregated_opex = df_opex.groupby(grouping_cols, as_index=False, dropna=False).agg(agg_logic)
        aggregated_opex['Component'] = 'Additional OPEX'

        # add aggregated OPEX back to CaCoCa dataframe
        df_cacoca = pd.concat([df_other, aggregated_opex], ignore_index=True)
    
    return df_cacoca

def filter_cacoca_dataframe(df_cacoca: pd.DataFrame) -> pd.DataFrame:
    """Keep only Type/Component combinations that align with the CaCoCa specification."""
    all_allowed_components = ALLOWED_COMPONENTS + ENERGY_TYPES + FEEDSTOCK_TYPES + EMISSION_TYPES
    
    # Find rows in df_translated with new types/components
    mask_type = df_cacoca["Type"].isin(ALLOWED_TYPES)
    mask_component = df_cacoca["Component"].isin(all_allowed_components)
    mask_valid = mask_type & mask_component

    # Warn about dropped rows
    dropped_rows = df_cacoca[~mask_valid]
    unexpected_dropped = dropped_rows[~dropped_rows["Type"].isin(EXPECTED_REMOVAL_TYPES)]
    if not unexpected_dropped.empty:
        unique_dropped = unexpected_dropped[["Type", "Component"]].drop_duplicates()
        print("Warning: Unexpected unique Type/Component combinations are dropped:")
        print(unique_dropped)

    # Keep only valid rows
    df_cacoca = df_cacoca[mask_valid]

    return df_cacoca

def save_cacoca_dataframe(df_cacoca: pd.DataFrame, target_folder: Path, posted_filename: str):
    """Save the translated CaCoCa dataframe as a CSV file in the target folder."""
    # ensure target folder exists
    target_folder.mkdir(parents=True, exist_ok=True)

    df_cacoca_path = target_folder / f"{posted_filename}.csv"
    df_cacoca.to_csv(df_cacoca_path, index=False)
