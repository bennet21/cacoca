import plotly as pl
import pandas as pd
import numpy as np
from .plot_tools import add_color, show_and_save, set_yrange_min_zero
from .plot_tools import display_name as dn, to_rgba
from ..setup.setup import Setup
from ..tools.tools import filter_df


def plot_absolute_hydrogen_demand(projects: pd.DataFrame,
                                  setup: Setup,
                                  project_names: list):

    projects = filter_df(projects, filter_by={'Project name': project_names})

    fig = pl.graph_objs.Figure()

    legend_title = dn('Project name')

    projects = add_color(
        projects=projects,
        by_column='Project name'
    )

    pdf = projects.query(f"`Project name` == '{project_names[0]}'")
    h2sum = np.zeros_like(pdf['Absolute Hydrogen Demand (t)'].values)
    # empty base
    fig = fig.add_scatter(
        x=projects['Period'],
        y=h2sum,
        mode='lines',
        line=dict(width=0),
        hoverinfo='skip',
        showlegend=False
    )

    for i, project_name in enumerate(project_names):

        pdf = projects.query(f"`Project name` == '{project_name}'")
        color = pdf['color'].values[0]

        if '(+2)' in project_name:
            alpha = 0.2
            dash = 'dot'
        else:
            alpha = 0.4
            dash = 'solid'

        rgba = to_rgba(color, alpha)

        h2sum += pdf['Absolute Hydrogen Demand (t)'].values

        fig = fig.add_scatter(
            x=pdf['Period'],
            y=h2sum,
            mode='lines',
            fill='tonexty',
            fillcolor=rgba,
            line=dict(color=color, width=3, dash=dash),
            marker=dict(size=0),
            name=dn(project_name),
            showlegend=True,
            hoverinfo='text',
            hovertext=dn(project_name)
        )
        if i == 3:
            fig = fig.add_scatter(
                x=pdf['Period'],
                y=h2sum,
                mode='lines',
                line=dict(color='rgb(0,0,0)', width=5, dash='dot'),
                name=dn('IPCEI'),
                showlegend=True,
                hoverinfo='text',
                hovertext=dn('IPCEI')
            )

    fig.update_layout(legend=dict(title=legend_title),
                      title=dn('Absolute Hydrogen Demand (t)'))
    # fig.update_xaxes(title='Jahr')
    set_yrange_min_zero(fig)
    fig.update_yaxes(title='t Hydrogen / yr')
    show_and_save(fig, setup.config, 'absolute_hydrogen_demand')
