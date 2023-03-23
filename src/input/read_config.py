import yaml
import numpy as np

def read_config(filepath: str): 
    with open(filepath, 'r') as f: 
        file_content = f.read()
    config = yaml.load(file_content, Loader=yaml.CLoader)
    config['years'] = np.arange(config['start_year'], config['end_year']+1)
    return config

if __name__ == '__main__': 
    config = read_config('config/config.yml')
    print(config)