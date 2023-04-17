import pandas as pd
import os

def read_projects(filepath: str, default_wacc: float):
    projects = pd.read_excel(filepath, sheet_name='Projects')
    projects = projects.query("Active == 1")
    projects = projects.fillna({'WACC': default_wacc})
    return projects


#if __name__ == '__main__':
#    config = read_projects('config/projects.xlsx', 0.06)
#    print(config)

def read_all_technologies(dirpath: str):
    basic_chemicals = pd.read_csv(os.path.join(dirpath, 'basic_chemicals.csv'), encoding="utf-8")
    cement = pd.read_csv(os.path.join(dirpath, 'cement.csv'), encoding="utf-8")
    other_industries = pd.read_csv(os.path.join(dirpath, 'other_industries.csv'), encoding="utf-8")
    steel_dri = pd.read_csv(os.path.join(dirpath, 'steel_dri.csv'), encoding="utf-8")
    steel = pd.read_csv(os.path.join(dirpath, 'steel.csv'), encoding="utf-8")

    basic_chemicals['Sector'] = "Basic Chemicals"
    cement['Sector'] = "Cement"
    other_industries['Sector'] = "Other Industries"
    steel_dri['Sector'] = "Steel DRI"
    steel['Sector'] = "Steel"

    technologies = (pd.concat([basic_chemicals, cement,other_industries,steel_dri,steel])
                    .filter(items=['Sector','Technology']))
    return technologies

read_all_technologies('data/tech/isi/')
