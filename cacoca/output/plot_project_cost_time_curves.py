import plotly as pl
import pandas as pd
from .plot_tools import add_color, show_and_save, set_yrange_min_zero
from .plot_tools import display_name as dn


def plot_project_cost_time_curves(projects: pd.DataFrame,
                                  config: dict,
                                  color_by: str = 'Project name',
                                  print_name: str = None,
                                  one_per_color: bool = False,
                                  **filter_by: dict):

    fig = pl.graph_objs.Figure()

    legend_title = dn(color_by)

    for filter_column, filter_values in filter_by.items():
        query_str = " | ".join([f"`{filter_column}` == '{fv}'" for fv in filter_values])
        projects = projects.query(query_str)

    projects = add_color(
        projects=projects,
        by_column=color_by
    )

    legend_names = set()
    for project_name, pdf in projects.groupby('Project name'):
        color = pdf['color'].values[0]
        legend_name = pdf[color_by].values[0]
        showlegend = legend_name not in legend_names
        legend_names.add(legend_name)
        if one_per_color and not showlegend:
            continue

        plot_project(fig,
                     pdf,
                     vname='Abatement_cost',
                     legend_name=dn(legend_name),
                     hovername=dn(project_name),
                     color=color,
                     showlegend=showlegend)

    p1 = projects.query(f"`Project name`=='{projects['Project name'].values[0]}'")

    plot_project(fig,
                 p1,
                 vname='Effective CO2 Price',
                 legend_name=dn('Effective CO2 Price'),
                 hovername=dn('Effective CO2 Price'),
                 color="#000000")

    # TODO: dotted, no uncertainty, only if different from effective
    # plot_project(fig,
    #              p1,
    #              vname='CO2 Price',
    #              legend_name='CO2 Price',
    #              hovername='CO2 Price',
    #              color="#000000")

    fig.update_layout(legend=dict(title=legend_title),
                      title=f"{dn('Abatement_cost')} ({dn(print_name)})")
    # fig.update_xaxes(title='Jahr')
    set_yrange_min_zero(fig)
    fig.update_yaxes(title='€ / t CO2')
    show_and_save(fig, config, 'cost_diff_curve_' + print_name)


def plot_project(fig: pl.graph_objs.Figure, df: pd.DataFrame, vname: str, legend_name: str,
                 hovername: str, color: str, showlegend: bool = True, emphasize: str = 'all_equal'):

    if emphasize == 'main':
        width = 8
        dash = 'solid'
        alpha = 0.4
        legendrank = 999
    elif emphasize == 'other':
        width = 2
        dash = 'dot'
        alpha = 0.0
        legendrank = 1001
    elif emphasize == 'all_equal':
        width = 3
        dash = 'solid'
        alpha = 0.4
        legendrank = 1000
    else:
        raise Exception("Invalid value for 'emphasize'")

    fig = fig.add_scatter(
        x=df['Period'],
        y=df[vname],
        mode='lines',
        line=dict(color=color, width=width, dash=dash),
        name=legend_name,
        showlegend=showlegend,
        hoverinfo='text',
        hovertext=hovername,
        legendrank=legendrank
    )
    vnl, vnu = vname + '_lower', vname + '_upper'
    if not (vnl in df.columns and vnu in df.columns):
        return fig

    if isinstance(color, tuple):
        rgba = f"rgba{color + (alpha,)}"
    elif color.startswith("#"):
        rgba = f"rgba{pl.colors.hex_to_rgb(color) + (alpha,)}"
    else:
        rgba = color.replace("rgb", "rgba").replace(")", f", {alpha})")

    fig = fig.add_scatter(
        x=df['Period'],
        y=df[vname + '_lower'],
        mode='lines',
        line=dict(width=0),
        hoverinfo='skip',
        showlegend=False
    )

    fig = fig.add_scatter(
        x=df['Period'],
        y=df[vname + '_upper'],
        mode='lines',
        fill='tonexty',
        fillcolor=rgba,
        line=dict(width=0),
        marker=dict(size=0),
        hoverinfo='skip',
        showlegend=False
    )
    return fig
