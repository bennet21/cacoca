import plotly as pl
import pandas as pd
import numpy as np
from src.output.plot_tools import show_and_save
from src.output.plot_tools import display_name as dn


def plot_stacked_bars(projects: pd.DataFrame, project_name: str):

    years = [2025, 2030, 2035, 2040, 2045]

    fig = pl.graph_objs.Figure()

    projects = projects.query(f"`Project name` == '{project_name}'")

    years = np.intersect1d(years, projects['Period'].values)
    query_str = " | ".join(f"Period == {y}" for y in years)
    projects = projects.query(query_str).drop_duplicates()

    non_feedstock_variables = ['CAPEX annuity', 'Additional OPEX', 'Effective CO2 Price']
    variables = non_feedstock_variables + \
        [cn for cn in projects.columns if str(cn).startswith('cost_')
            and not str(cn).endswith(('_variance', '_diff', '_ref', '_upper', '_lower'))]

    # Hack: Bring Effective CO2 Price in form to be added to reference, divided by emissions diff
    projects = projects.assign(**{
        'Effective CO2 Price_ref': lambda df: df['Effective CO2 Price'] * -df['Emissions_diff'],
        'Effective CO2 Price': 0.})

    pmax = projects.max()
    variables = [vn for vn in variables if max(pmax[vn], pmax[vn + '_ref']) > 1.e-6]

    # colors = get_color(variables + ['Effective CO2 Price'])
    width = 1.5

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
        'Effective CO2 Price': 'rgb(0.2, 0.2, 0.2)'
    }

    for v in variables:
        vn = v.replace('cost_', '')
        if vn not in colors:
            raise Exception(f"Variable {vn} not found in colors dict")

    base = 0. * projects["CAPEX annuity"]
    base_ref = 0. * projects["CAPEX annuity_ref"]
    for vn, color in colors.items():

        cn = vn if vn in non_feedstock_variables else 'cost_' + vn
        if cn not in variables:
            continue

        fig.add_bar(
            name=dn(vn),
            # x=[projects['Period'].to_list(), ['Vorhaben' for _ in years]],
            x=projects['Period'],
            y=projects[cn] / -projects['Emissions_diff'],
            offsetgroup=0,
            base=base,
            marker_color=color,
            width=width
        )
        base += projects[cn] / -projects['Emissions_diff']

        fig.add_bar(
            name=dn(vn),
            # x=[projects['Period'].to_list(), ['Referenz' for _ in years]],
            x=projects['Period'],
            y=projects[cn + '_ref'] / -projects['Emissions_diff'],
            offsetgroup=1,
            base=base_ref,
            marker_color=color,
            width=width,
            showlegend=False
        )
        base_ref += projects[cn + '_ref'] / -projects['Emissions_diff']

    offsets = [-1., 1.]
    toplines = [base, base_ref]
    linecolors = [pl.colors.qualitative.Dark24[10], 'rgb(0., 0., 0.)']
    for offset, y, linecol in zip(offsets, toplines, linecolors):
        fig.add_scatter(
            x=projects['Period'] + offset,
            y=y,
            mode='lines',
            line=dict(color=linecol, width=2, dash='solid'),
            showlegend=False,
        )

    fig.update_yaxes(title='€/t CO2')
    fig.update_layout(legend_traceorder="reversed",
                      title=f"Kostenvergleich {dn(project_name)}")
    # fig.update_layout(barmode="relative")
    show_and_save(fig, 'stacked_bars_' + project_name)
