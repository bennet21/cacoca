import sys
sys.path.append("../cacoca")
from src.tools.gaussian import add_variance
from read_scenario_data import read_all_scenario_data
import pandas as pd


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', None)

data, h2share = read_all_scenario_data(sys.argv[1]) #data/scenarios/isi/
print(h2share.filter(["Scenario"]))