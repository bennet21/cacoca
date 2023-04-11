# %%
import sys
import os
import plotly as pl
import pandas as pd
repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(repo_dir)
# import pandas as pd
from src.input.read_scenario_data import read_all_scenario_data, years_to_rows, add_variance
from src.input.read_config import read_config
from src.input.read_projects import read_projects
from src.output.plot_project_cost_time_curves import plot_project, add_color
from src.tools.gaussian import get_bounds
from config.project_list_ALL import project_name

# CONFIG --------------------

config_filepath = os.path.join(repo_dir, 'config', 'config_all.yml')
projects_filepath = os.path.join(repo_dir, 'config', 'Projects_ALL.xlsx')
scen_dir_path = os.path.join(repo_dir, 'data', 'scenarios', 'isi_all')
# Project name is in config/project_lsit_ALL.py
print_other = True

# ---------------------------

config = read_config(config_filepath)
config = config["scenarios_actual"]

if project_name:
    projects = read_projects(projects_filepath, 0.0)
    h2share_scen = projects \
        .query(f"`Project name` == '{project_name}'")["H2 Share Scenario"] \
        .values[0]
    config["Prices H2 Share"] = h2share_scen

data_all, h2share = read_all_scenario_data(dirpath=scen_dir_path)

prices = years_to_rows(
    data_all.prices, year_name="Period", value_name="Price"
)
prices = prices.drop(columns='Source Reference')

# Hack to make it fit in price plotting scheme below
h2share = years_to_rows(h2share, year_name="Period", value_name="Price")
h2share["Component"] = "H2 Share"
h2share["Unit"] = "H2 Share"

prices = pd.concat([prices, h2share])

add_variance(prices, mode='h2_and_co2_sigma0.2')
prices = get_bounds(prices)


free_allocations = years_to_rows(
    data_all.free_allocations, year_name="Period", value_name="Free Allocations"
)

for component_name, cdf in prices.groupby('Component'):

    fig = pl.graph_objs.Figure()

    cdf = add_color(
        cdf,
        by_column='Scenario'
    )

    for scenario_name, sdf in cdf.groupby('Scenario'):
        color = sdf['color'].values[0]
        legend_name = scenario_name

        if "Prices " + component_name in config:
            if config["Prices " + component_name] == scenario_name:
                emphasize = 'main'
            else:
                emphasize = 'other'
                if not print_other:
                    continue
        else:
            emphasize = None

        plot_project(fig,
                     sdf,
                     vname='Price',
                     legend_name=legend_name,
                     hovername=scenario_name,
                     color=color,
                     emphasize=emphasize)

    fig.update_layout(legend=dict(title='Szenario'),
                      title=component_name)
    fig.update_xaxes(title='Jahr')
    fig.update_yaxes(title=sdf['Unit'].values[0])
    fig.show()

    # %%
