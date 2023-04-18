import plotly as pl
import pandas as pd
import numpy as np
from src.output.plot_tools import show_and_save
from src.output.plot_tools import display_name as dn


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


def plot_stacked_bars(projects: pd.DataFrame, project_name: str, cost_per: str = 'product'):

    if cost_per == 'product':
        yunit = '€/t product'
        co2pricename = 'CO2 Cost'
    elif cost_per == 'em_savings':
        yunit = '€/t CO2'
        co2pricename = 'Effective CO2 Price'
    else:
        raise Exception(f'Invalid parameter cost_per={cost_per}')

    years = [2025, 2030, 2035, 2040, 2045]

    fig = pl.graph_objs.Figure()

    projects = projects.query(f"`Project name` == '{project_name}'")

    years = np.intersect1d(years, projects['Period'].values)
    query_str = " | ".join(f"Period == {y}" for y in years)
    projects = projects.query(query_str).drop_duplicates()

    non_feedstock_variables = ['CAPEX annuity', 'Additional OPEX', co2pricename]
    variables = non_feedstock_variables + \
        [cn for cn in projects.columns if str(cn).startswith('cost_')
            and not str(cn).endswith(('_variance', '_diff', '_ref', '_upper', '_lower'))]

    # Hack: Bring Effective CO2 Price in form to be added to reference, divided by emissions diff
    projects = projects.assign(**{
        co2pricename + '_ref': lambda df: df['Effective CO2 Price'] * -df['Emissions_diff'],
        co2pricename: 0.})

    if cost_per == 'em_savings':
        for vn in variables:
            projects[vn] /= -projects['Emissions_diff']
            projects[vn + '_ref'] /= -projects['Emissions_diff']

    pmax = projects.max()
    variables = [vn for vn in variables if max(pmax[vn], pmax[vn + '_ref']) > 1.e-6]

    # colors = get_color(variables + ['Effective CO2 Price'])
    width = 0.9

    for v in variables:
        vn = v.replace('cost_', '')
        if vn not in colors:
            raise Exception(f"Variable {vn} not found in colors dict")

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

    offsetnames = ['Vorhaben', 'Referenz']
    bases = [yzero(), yzero()]
    suffixes = ['', '_ref']
    showlegend = [True, False]
    linecolors = [pl.colors.qualitative.Dark24[10], 'rgb(0., 0., 0.)']

    for vn, color in colors.items():

        cn = vn if vn in non_feedstock_variables else 'cost_' + vn
        if cn not in variables:
            continue

        for ibar in range(2):
            fig.add_bar(
                name=dn(vn),
                x=[projects['Period'].to_list(), [offsetnames[ibar] for _ in years]],
                y=projects[cn + suffixes[ibar]],
                base=bases[ibar],
                marker_color=color,
                width=width,
                showlegend=showlegend[ibar]
            )
            bases[ibar] += projects[cn + suffixes[ibar]]

    for ibar in range(2):
        fig.add_scatter(
            x=[projects['Period'].to_list(), [offsetnames[ibar] for _ in years]],
            y=bases[ibar],
            mode='lines',
            line=dict(color=linecolors[ibar], width=2, dash='solid'),
            showlegend=False,
        )

    add_placeholder(1)

    fig.update_yaxes(title=yunit)
    fig.update_layout(legend_traceorder="reversed",
                      title=f"Kostenvergleich {dn(project_name)}")
    fig.update_layout(barmode="relative")
    show_and_save(fig, 'stacked_bars_' + project_name)

