import pandas as pd


def read_projects(filepath: str, default_wacc: float):
    projects = pd.read_excel(filepath, sheet_name='Projects')
    projects['WACC'].fillna(default_wacc, inplace=True)
    return projects


if __name__ == '__main__':
    config = read_projects('config/projects.xlsx', 0.06)
    print(config)
