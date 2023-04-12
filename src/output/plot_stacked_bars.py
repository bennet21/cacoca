import plotly as pl
import pandas as pd
import numpy as np
from src.output.plot_tools import get_color, show_and_save


def plot_stacked_bars(projects: pd.DataFrame, project_name: str):

    years = [2025, 2030, 2035, 2040, 2045]

    fig = pl.graph_objs.Figure()

    projects = projects.query(f"`Project name` == '{project_name}'")

    years = np.intersect1d(years, projects['Period'].values)
    query_str = " | ".join(f"Period == {y}" for y in years)
    projects = projects.query(query_str).drop_duplicates()

    variables = ['CAPEX annuity', 'Additional OPEX'] + \
        [cn for cn in projects.columns if str(cn).startswith('cost_')
            and not str(cn).endswith(('_variance', '_diff', '_ref', '_upper', '_lower'))]

    pmax = projects.max()
    variables = [vn for vn in variables if max(pmax[vn], pmax[vn + '_ref']) > 1.e-6]
    colors = get_color(variables + ['Effective CO2 Price'])
    width = 1.5

    # colors = {
    #     'CAPEX annuity': ,
    #     'Additional OPEX': ,
    #     'Coking Coal': ,
    #     'DRI-Pellets': ,
    #     'Electricity': ,
    #     'Hydrogen': ,
    #     'Injection Coal': ,
    #     'Naphta': ,
    #     'Natural Gas': ,
    #     'Scrap Steel':
    # }

    base = 0. * projects["CAPEX annuity"]
    base_ref = 0. * projects["CAPEX annuity_ref"]
    for vn, color in zip(variables, colors):

        component = vn.replace("cost_", "")
        fig.add_bar(
            name=component,
            # x=[projects['Period'].to_list(), ['Vorhaben' for _ in years]],
            x=projects['Period'],
            y=projects[vn] / -projects['Emissions_diff'],
            offsetgroup=0,
            base=base,
            marker_color=color,
            width=width
        )
        base += projects[vn] / -projects['Emissions_diff']

        fig.add_bar(
            name=component,
            # x=[projects['Period'].to_list(), ['Referenz' for _ in years]],
            x=projects['Period'],
            y=projects[vn + '_ref'] / -projects['Emissions_diff'],
            offsetgroup=1,
            base=base_ref,
            marker_color=color,
            width=width,
            showlegend=False
        )
        base_ref += projects[vn + '_ref'] / -projects['Emissions_diff']

    fig.add_bar(
        name="Effective CO2 Price",
        # x=[projects['Period'].to_list(), ['Referenz' for _ in years]],
        x=projects['Period'],
        y=projects['Effective CO2 Price'],
        offsetgroup=1,
        base=base_ref,
        marker_color=colors[-1],
        width=width
    )

    fig.update_yaxes(title='€/t CO2')
    fig.update_layout(legend_traceorder="reversed",
                      title=f"{project_name} ({projects['Industry'].values[0]})")
    # fig.update_layout(barmode="relative")
    show_and_save(fig, 'stacked_bars_' + project_name)
