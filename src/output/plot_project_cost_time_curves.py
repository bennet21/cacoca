import plotly as pl
import pandas as pd
from src.output.plot_tools import add_color


def plot_project_cost_time_curves(projects: pd.DataFrame, sector: str = None,
                                  project_names: list = None):

    fig = pl.graph_objs.Figure()

    if sector:
        color_column = 'Project name'
        projects = projects.query(f"Industry == '{sector}'")
        legend_title = 'Projekt'
    else:
        color_column = 'Industry'
        sector = ""
        legend_title = "Sektor"

    if project_names:
        query_str = " | ".join([f"`Project name` == '{pn}'" for pn in project_names])
        projects = projects.query(query_str)

    projects = add_color(
        projects=projects,
        by_column=color_column
    )

    legend_names = set()
    for project_name, pdf in projects.groupby('Project name'):
        color = pdf['color'].values[0]
        legend_name = pdf[color_column].values[0]
        showlegend = legend_name not in legend_names
        legend_names.add(legend_name)
        # if legend_name != 'steel_dri':
        #     continue
        if not showlegend:
            continue

        plot_project(fig,
                     pdf,
                     vname='Abatement_cost',
                     legend_name=legend_name,
                     hovername=project_name,
                     color=color,
                     showlegend=showlegend)

    p1 = projects.query(f"`Project name`=='{projects['Project name'].values[0]}'")

    plot_project(fig,
                 p1,
                 vname='Effective CO2 Price',
                 legend_name='Effective CO2 Price',
                 hovername='Effective CO2 Price',
                 color="#000000")

    # TODO: dotted, no uncertainty, only if different from effective
    # plot_project(fig,
    #              p1,
    #              vname='CO2 Price',
    #              legend_name='CO2 Price',
    #              hovername='CO2 Price',
    #              color="#000000")

    fig.update_layout(legend=dict(title=legend_title),
                      title="Vermediungskosten " + sector)
    fig.update_xaxes(title='Jahr')
    fig.update_yaxes(title='€/t CO2')
    fig.show()


def plot_project(fig: pl.graph_objs.Figure, df: pd.DataFrame, vname: str, legend_name: str,
                 hovername: str, color: str, showlegend: bool = True, emphasize=None):

    if emphasize == 'main':
        width = 3
        dash = 'solid'
        alpha = 0.4
    elif emphasize == 'other':
        width = 1
        dash = 'dot'
        alpha = 0.1
    else:
        width = 2
        dash = 'solid'
        alpha = 0.4

    fig = fig.add_scatter(
        x=df['Period'],
        y=df[vname],
        mode='lines',
        line=dict(color=color, width=width, dash=dash),
        name=legend_name,
        showlegend=showlegend,
        hoverinfo='text',
        hovertext=hovername
    )
    vnl, vnu = vname + '_lower', vname + '_upper'
    if not (vnl in df.columns and vnu in df.columns):
        return fig
    fig = fig.add_scatter(
        x=df['Period'],
        y=df[vname + '_lower'],
        line=dict(width=0),
        hoverinfo='skip',
        showlegend=False
    )

    if isinstance(color, tuple):
        rgba = f"rgba{color + (alpha,)}"
    elif color.startswith("#"):
        rgba = f"rgba{pl.colors.hex_to_rgb(color) + (alpha,)}"
    else:
        rgba = color.replace("rgb", "rgba").replace(")", f", {alpha})")

    fig = fig.add_scatter(
        x=df['Period'],
        y=df[vname + '_upper'],
        fill='tonexty',
        fillcolor=rgba,
        line=dict(width=0),
        hoverinfo='skip',
        showlegend=False
    )
    return fig
