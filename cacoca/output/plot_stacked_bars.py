import plotly as pl
import pandas as pd
import numpy as np
from .plot_tools import show_and_save
from .plot_tools import display_name as dn


# The dict also prescribes the ordering in the plot (from bottom to top):
# CAPEX, OPEX, non-energy feedstock, energy carriers, CO2 price
colors = {
    'CAPEX annuity': 'rgb(0.4, 0.4, 0.4)',
    'Additional OPEX': 'rgb(0.7, 0.7, 0.7)',
    'Iron Ore': pl.colors.qualitative.Dark24[3],
    'DRI-Pellets': pl.colors.qualitative.Dark24[4],
    'Scrap Steel': pl.colors.qualitative.Dark24[14],
    'Naphta': pl.colors.qualitative.Dark24[17],
    'Coking Coal': pl.colors.qualitative.Dark24[16],
    'Injection Coal': pl.colors.qualitative.Dark24[6],
    'Natural Gas': pl.colors.qualitative.Dark24[13],
    'Hydrogen': pl.colors.qualitative.Dark24[0],
    'Electricity': pl.colors.qualitative.Dark24[2],
    'Effective CO2 Price': 'rgb(0.2, 0.2, 0.2)',
    'CO2 Cost': 'rgb(0.2, 0.2, 0.2)'
}


def plot_stacked_bars(projects: pd.DataFrame, config: dict, project_name: str,
                      cost_per: str = 'product', is_diff: bool = False):

    if cost_per == 'product':
        yunit = '€/t Produkt'
        co2pricename = 'CO2 Cost'
    elif cost_per == 'em_savings':
        yunit = '€/t CO2'
        co2pricename = 'Effective CO2 Price'
    else:
        raise Exception(f'Invalid parameter cost_per={cost_per}')

    projects = projects.query(f"`Project name` == '{project_name}'")

    years = [2025, 2030, 2035, 2040, 2045]
    years = np.intersect1d(years, projects['Period'].values)
    query_str = " | ".join(f"Period == {y}" for y in years)
    projects = projects.query(query_str).drop_duplicates()

    # Hack: Bring Effective CO2 Price in form to be added to reference, divided by emissions diff
    projects = projects.assign(**{
        co2pricename + '_ref': lambda df: df['Effective CO2 Price'] * -df['Emissions_diff'],
        co2pricename: 0.})

    variables = ['CAPEX annuity', 'Additional OPEX'] \
        + [cn for cn in projects.columns if str(cn).startswith('cost_')
           and not str(cn).endswith(('_variance', '_diff', '_ref', '_upper', '_lower'))]
    if not is_diff:
        variables.append(co2pricename)

    if cost_per == 'em_savings':
        for vn in variables:
            projects[vn] /= -projects['Emissions_diff']
            projects[vn + '_ref'] /= -projects['Emissions_diff']

    pmax = projects.max()
    variables = [vn for vn in variables if max(pmax[vn], pmax[vn + '_ref']) > 1.e-6]

    # colors = get_color(variables + ['Effective CO2 Price'])
    width = 0.9

    fig = pl.graph_objs.Figure()

    def yzero():
        return 0. * projects['CAPEX annuity']

    def add_placeholder(id: int):
        fig.add_bar(
            name='',
            x=[projects['Period'].to_list(), [' ' * id for _ in years]],
            y=yzero(),
            offsetgroup=id,
            base=0.,
            width=width,
            showlegend=False
        )

    add_placeholder(0)

    legend_vars = set()

    projects_new = projects \
        .filter(['Period'] + variables) \
        .rename(columns=lambda cn: str(cn).replace('cost_', ''))
    projects_ref = projects \
        .filter(['Period'] + [vn + '_ref' for vn in variables]) \
        .rename(columns=lambda cn: str(cn).replace('cost_', '').replace('_ref', ''))
    projects_co2price = projects \
        .filter(['Period', co2pricename + '_ref']) \
        .rename(columns={co2pricename + '_ref': co2pricename})

    class Bar():
        def __init__(self, name, projects: pd.DataFrame, linecolor=None, reversed=False, base=None):
            self.name = name
            self.projects = projects
            self.vnames = set(self.projects.columns) - {'Period'}
            self.linecolor = linecolor
            self.dir = -1 if reversed else 1
            self.base = yzero() if base is None else base

    if not is_diff:
        new = Bar(name='Vorhaben',
                  projects=projects_new,
                  linecolor=pl.colors.qualitative.Dark24[10])
        ref = Bar(name='Referenz',
                  projects=projects_ref,
                  linecolor='rgb(0., 0., 0.)')
        bars = [new, ref]
    else:
        new = Bar(name='Vorhaben',
                  projects=projects_new)
        ref = Bar(name='Referenz',
                  projects=projects_ref,
                  linecolor=pl.colors.qualitative.Dark24[10],
                  reversed=True,
                  base=new.base)
        co2 = Bar(name='CO2-Preis',
                  projects=projects_co2price,
                  linecolor='rgb(0., 0., 0.)')
        bars = [new, ref, co2]

    for bar in bars:

        for vn in bar.vnames:
            if vn not in colors:
                raise Exception(f"Variable {vn} not found in colors dict")

        for vn, color in list(colors.items())[::bar.dir]:

            if vn not in bar.vnames:
                continue

            fig.add_bar(
                name=dn(vn),
                x=[bar.projects['Period'].to_list(), [bar.name for _ in years]],
                y=bar.dir * bar.projects[vn],
                base=bar.base,
                marker_color=color,
                width=width,
                showlegend=vn not in legend_vars
            )
            legend_vars.add(vn)
            bar.base += bar.dir * bar.projects[vn]

        if bar.linecolor:
            fig.add_scatter(
                x=[bar.projects['Period'].to_list(), [bar.name for _ in years]],
                y=bar.base,
                mode='lines',
                line=dict(color=bar.linecolor, width=2, dash='solid'),
                showlegend=False,
            )

    add_placeholder(1)

    fig.update_yaxes(title=yunit)
    fig.update_layout(legend_traceorder="reversed",
                      title=f"Kostenvergleich {dn(project_name)}")
    fig.update_layout(barmode="relative")
    show_and_save(fig, config, 'stacked_bars_' + project_name)
