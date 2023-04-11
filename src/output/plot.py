import plotly as pl
import pandas as pd


def plot_all(projects: pd.DataFrame, filename: str = None):

    fig = pl.graph_objs.Figure()

    projects = add_color(
        projects,
        by_column='Industry',
        cmap=pl.colors.qualitative.D3
    )

    legend_names = set()
    for project_name, pdf in projects.groupby('Project name'):
        color = pdf['color'].values[0]
        legend_name = pdf['Industry'].values[0]
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
                 legend_name='CO2 Price',
                 hovername='CO2 Price',
                 color="#000000")

    fig.update_layout(legend=dict(title='Sektor'))
    fig.update_xaxes(title='Jahr')
    fig.update_yaxes(title='€/t CO2')
    fig.show()


def plot_project(fig: pl.graph_objs.Figure, df: pd.DataFrame, vname: str, legend_name: str,
                 hovername: str, color: str, showlegend: bool = True):

    fig = fig.add_scatter(
        x=df['Period'],
        y=df[vname],
        mode='lines',
        line=dict(color=color),
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
    fig = fig.add_scatter(
        x=df['Period'],
        y=df[vname + '_upper'],
        fill='tonexty',
        fillcolor=f"rgba{pl.colors.hex_to_rgb(color) + (0.4,)}",
        line=dict(width=0),
        hoverinfo='skip',
        showlegend=False
    )
    return fig


# define colors to use
def add_color(projects: pd.DataFrame, by_column: str, cmap: list):
    colors = projects.filter([by_column]).drop_duplicates()
    colors['color'] = cmap[:colors.shape[0]]
    projects = projects.merge(colors, how='left', on=[by_column])
    return projects
