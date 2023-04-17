import pandas as pd
from src.input.read_config import read_config
from src.input.read_projects import read_projects
from src.input.read_techdata import read_techdata
from src.input.read_scenario_data import read_raw_scenario_data


class Setup():

    def __init__(self, config: dict, projects_all: pd.DataFrame, techdata: pd.DataFrame,
                 reference_tech: pd.DataFrame, scendata_raw: pd.DataFrame,
                 h2share_raw: pd.DataFrame) -> None:
        self.config = config
        self.projects_all = projects_all
        self.techdata = techdata
        self.reference_tech = reference_tech
        self.scendata_raw = scendata_raw
        self.h2share_raw = h2share_raw
        return


def get_setup(config_filepath: str = None, config: dict = None):

    if bool(config_filepath) == bool(config):
        raise Exception('Specify either config_filepath or config dict.')
    if bool(config_filepath):
        config = read_config(config_filepath)

    mode = config['mode']
    if mode not in ['analyze_cost', 'auction']:
        raise Exception('Invalid mode')

    projects_all = read_projects(
        config['projects_file'],
        config['default_wacc']
    )

    techdata, reference_tech = read_techdata(
        config['techdata_dir'],
        config['techdata_files']
    )

    scendata_raw, h2share_raw = read_raw_scenario_data(dirpath=config['scenarios_dir'])

    return Setup(config, projects_all, techdata, reference_tech, scendata_raw, h2share_raw)
