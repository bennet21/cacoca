import pandas as pd
import sys
sys.path.append("../cacoca")
from src.setup.read_input import read_techdata, read_raw_scenario_data

# usage: get_dropdown_options.py <mode> <input_dir>

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

mode = sys.argv[1]
dirpath = sys.argv[2]

if mode == 'Technologies':

    sectors = [
        "Basic Chemicals",
        "Cement",
        "Other Industries",
        "Steel DRI",
        "Steel"
    ]

    technologies, _ = read_techdata(dirpath, [str(s).lower().replace(" ", "_") for s in sectors])
    technologies = technologies \
        .filter(items=['Industry', 'Technology']) \
        .rename(columns={'Industry': 'Sector'})
    print(technologies)

elif mode == 'H2Share':

    _, _, h2share = read_raw_scenario_data(dirpath)  # data/scenarios/isi/
    print(h2share.filter(["Scenario"]))

else:
    raise Exception('invalid mode')
