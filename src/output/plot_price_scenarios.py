# %%
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# import pandas as pd
from src.input.read_scenario_data import read_all_scenario_data, years_to_rows, add_variance
from src.output.plot import plot_project, add_color
from src.tools.gaussian import get_bounds
import plotly as pl


dirpath = '../../data/scenarios/isi'

data_all, h2share = read_all_scenario_data(dirpath=dirpath)

prices = years_to_rows(
    data_all.prices, year_name="Period", value_name="Price"
)
add_variance(prices, mode='h2_and_co2_sigma0.2')
prices = get_bounds(prices)


free_allocations = years_to_rows(
    data_all.free_allocations, year_name="Period", value_name="Free Allocations"
)

h2share = years_to_rows(h2share, year_name="Operation Year", value_name="H2 Share")

for component_name, cdf in prices.groupby('Component'):
    fig = pl.graph_objs.Figure()

    cdf = add_color(
        cdf,
        by_column='Scenario',
        cmap=pl.colors.qualitative.D3
    )

    for scenario_name, sdf in cdf.groupby('Scenario'):
        color = sdf['color'].values[0]
        legend_name = scenario_name

        plot_project(fig,
                     sdf,
                     vname='Price',
                     legend_name=legend_name,
                     hovername=scenario_name,
                     color=color)

    fig.update_layout(legend=dict(title='Szenario'),
                      title=component_name)
    fig.update_xaxes(title='Jahr')
    fig.update_yaxes(title=sdf['Unit'].values[0])
    fig.show()

    # %%
