from read_projects import read_all_technologies
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)
print(read_all_technologies('data/tech/isi/'))
#import pandas as pd
#print(pd.DataFrame({'A': ['apple', 'banana', 'orange'], 'B': [5, 10, 15]}))
#print("hallo")