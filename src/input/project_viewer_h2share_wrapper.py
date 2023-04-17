from read_scenario_data import read_all_scenario_data
import pandas as pd
import sys

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)
data, h2share = read_all_scenario_data(sys.argv[1]) #data/scenarios/isi/
print(h2share.filter(["Scenario"]))