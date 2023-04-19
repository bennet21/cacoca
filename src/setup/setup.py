import pandas as pd
from src.setup.read_input import read_config, read_projects, read_techdata, read_raw_scenario_data
from src.setup.select_scenario_data import select_scenario_data, select_h2share


class Setup():

    def __init__(self, config_filepath: str = None, config: dict = None):

        if config_filepath is None and config is not None:
            self.config = config
        elif config_filepath is not None and config is None:
            self.config = read_config(config_filepath)
        else:
            raise Exception('Specify either config_filepath or config dict.')

        if self.config['mode'] not in ['analyze_cost', 'auction']:
            raise Exception('Invalid mode')

        self.projects_all = read_projects(
            self.config['projects_file'],
            self.config['default_wacc']
        )

        self.techdata, self.reference_tech = read_techdata(
            self.config['techdata_dir'],
            self.config['techdata_files']
        )

        self.scendata_raw, self.h2share_raw = read_raw_scenario_data(
            dirpath=self.config['scenarios_dir'])

        return

    def select_scenario_data(self,
                             scenarios: dict,
                             relative_standard_deviation: dict = None,
                             absolute_standard_deviation: dict = None):
        if isinstance(scenarios, str):
            scenarios = self.config[scenarios]
        self.scendata = select_scenario_data(
            self.scendata_raw,
            scenarios,
            relative_standard_deviation,
            absolute_standard_deviation)

    def select_h2share(self,
                       projects: pd.DataFrame = None,
                       auction_year: int = None):
        if projects is None:
            projects = self.projects_all
        self.h2share = select_h2share(
            self.h2share_raw,
            projects,
            auction_year)
