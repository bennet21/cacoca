from src.setup.read_input import read_config, read_projects, read_techdata, read_raw_scenario_data
from src.setup.select_scenario_data import select_prices, select_free_allocations, select_h2share


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
        self.projects_current = self.projects_all

        self.techdata, self.reference_tech = read_techdata(
            self.config['techdata_dir'],
            self.config['techdata_files']
        )

        self.prices_raw, self.free_allocations_raw, self.h2share_raw \
            = read_raw_scenario_data(dirpath=self.config['scenarios_dir'])

        return

    def select_scenario_data(self, scenarios: dict):
        if isinstance(scenarios, str):
            scenarios = self.config[scenarios]
        self.prices = select_prices(self.prices_raw, scenarios)
        self.free_allocations = select_free_allocations(self.free_allocations_raw, scenarios)

    def select_h2share(self, auction_year: int = None):
        self.h2share = select_h2share(self.h2share_raw, self.projects_current, auction_year)
