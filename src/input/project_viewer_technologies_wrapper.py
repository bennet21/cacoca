from read_projects import read_all_technologies
import pandas as pd
import sys

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)
print(read_all_technologies(sys.argv[1])) #data/tech/isi/