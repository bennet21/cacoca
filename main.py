from src.input.read_config import read_config
from src.input.read_projects import read_projects
from src.input.read_techdata import read, expand_by_years
from src.input.read_scenario_data import read_scenario_data


# import sys
# config_filepath = sys.argv[1]
config_filepath = 'config/config.yml'

config = read_config(config_filepath)

projects = read_projects(config['projects_file'],
                         config['default_wacc'])

techdata = read(config['techdata_dir'], 
                config['techdata_files'] 
                )

techdata = expand_by_years(techdata, 
                           config['years'])

data_actual, data_bidding, h2share, cbam_factor = read_scenario_data(
    config['scenarios_dir'], 
    config['scenarios_actual'], 
    config['scenarios_bidding'] 
)
