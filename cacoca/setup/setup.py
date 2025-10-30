import numpy as np
import pandas as pd
from .read_input import read_config, read_projects, read_techdata, read_raw_scenario_data
from .select_scenario_data import select_prices, select_free_allocations, select_h2share


class Setup():
    """
    Container for the whole setup of a cacoca run, including a config dictionary and dataframes
    with all necessary data (description in the constructor);
    Prices, free allocations and h2share are read in as "raw" and can then be selected/modified by
    the class methods below.
    For the projects DF, a version with all projects and one with currently selected ones exists.
    """

    def __init__(self, config_filepath: str = None, config: dict = None):

        # parameter dictionary read in from a yml file
        self.config = None
        # df of tranformative projects and their properties/definition
        self.projects_all = None
        self.projects_current = None
        # techno-economic parameters (energy demands, costs, emissions) per technology
        self.techdata = None
        # reference technology under EU ETS
        self.reference_tech = None
        # time series for co2, energy carrier and feedstock prices
        self.prices_raw = None
        self.prices = None
        # ETS free allocations
        self.free_allocations_raw = None
        self.free_allocations = None
        # time series scenarios for share of 'new' fuel mix;
        # For steel_dri, this is the h2 share; for cement, the share with CCS
        self.h2share_raw = None
        self.h2share = None
        # absolute standard deviation scenarios for sensitivities implementation
        self.abs_std_raw = None

        if config_filepath is None and config is not None:
            self.config = config
        elif config_filepath is not None and config is None:
            self.config = read_config(config_filepath)
        else:
            raise Exception('Specify either config_filepath or config dict.')

        if self.config['mode'] not in ['analyze_cost', 'auction']:
            raise Exception('Invalid mode')

        self.all_years = pd.DataFrame.from_dict({'Period': np.arange(2020, 2061)})

        self.projects_all = read_projects(self.config)
        self.projects_current = self.projects_all

        self.techdata, self.reference_tech = read_techdata(
            self.config['techdata_dir'],
            self.config['techdata_files']
        )

        # h2_share is actually share of "new" fuel mix, name is slightly misleading
        # everything is read in as raw data first, scenarios later pick the relevant data
        self.prices_raw, self.free_allocations_raw, self.h2share_raw, self.abs_std_raw \
            = read_raw_scenario_data(dirpath=self.config['scenarios_dir'])

        return

    def select_scenario_data(self, scenarios: dict):
        """
        - Select by the scenario names given in the config;
        - Transform: Calendar years are columns in the raw data and rows in the selected data.
        """
        if isinstance(scenarios, str):
            scenarios = self.config[scenarios]
        self.prices = select_prices(self.prices_raw, scenarios)
        self.free_allocations = select_free_allocations(self.free_allocations_raw, scenarios)

    def select_h2share(self, auction_year: int = None):
        """
        - Select by the h2 share scenario names given in the projects df for each project
        - Transform: Ooperation years are columns in the raw data and rows in the selected data.
        """
        self.h2share = select_h2share(self.h2share_raw, self.projects_current, auction_year)
