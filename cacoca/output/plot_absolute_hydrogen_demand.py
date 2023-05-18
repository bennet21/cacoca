import plotly as pl
import pandas as pd
from .plot_tools import add_color, show_and_save, set_yrange_min_zero
from .plot_tools import display_name as dn
from .plot_project_cost_time_curves import plot_project
from ..setup.setup import Setup
from ..tools.tools import filter_df


def plot_absolute_hydrogen_demand(projects: pd.DataFrame,
                                  setup: Setup,
                                  print_name: str = None,
                                  **filter_by: dict):

    projects = filter_df(projects, filter_by=filter_by)

    fig = pl.graph_objs.Figure()

    legend_title = dn('Project name')

    projects = add_color(
        projects=projects,
        by_column='Project name'
    )

    for project_name, pdf in projects.groupby('Project name'):
        color = pdf['color'].values[0]
        legend_name = dn(project_name)

        plot_project(fig,
                     pdf,
                     vname='Absolute Hydrogen Demand (t)',
                     legend_name=dn(legend_name),
                     hovername=dn(project_name),
                     color=color)

    fig.update_layout(legend=dict(title=legend_title),
                      title=f"{dn('Absolute Hydrogen Demand (t)')} ({dn(print_name)})")
    # fig.update_xaxes(title='Jahr')
    set_yrange_min_zero(fig)
    fig.update_yaxes(title='t Hydrogen / yr')
    show_and_save(fig, setup.config, 'absolute_hydrogen_demand_' + print_name)
