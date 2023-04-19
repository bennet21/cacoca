from src.setup.read_input import read_config, read_projects, read_techdata, read_raw_scenario_data


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
