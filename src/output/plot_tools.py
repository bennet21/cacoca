import plotly as pl
import pandas as pd


# define colors to use
def add_color(projects: pd.DataFrame = None, by_column: str = None):

    colors = projects.filter([by_column]).drop_duplicates()
    colors['color'] = get_color(colors[by_column].values.tolist())
    projects = projects.merge(colors, how='left', on=[by_column])

    return projects


def get_color(variables: list):
    n_scen = len(variables)
    if n_scen <= 10:
        cmap = pl.colors.qualitative.D3
    elif n_scen <= 24:
        cmap = pl.colors.qualitative.Dark24
    else:
        cmap = pl.colors.sample_colorscale('Viridis', n_scen + 1, colortype='rgb')

    return cmap[:n_scen]


def set_yrange_min_zero(fig: pl.graph_objs.Figure):
    yrange = list(fig.full_figure_for_development(warn=False).layout.yaxis.range)
    yrange[0] = min(yrange[0], -0.04 * yrange[1])
    yrange[1] = max(yrange[1], 1.04 * yrange[1])
    fig.update_yaxes(range=yrange)


def show_and_save(fig: pl.graph_objs.Figure, base_name: str = None):
    fig.show()
    if base_name:
        dir_path = 'output/'
        # fig.update_xaxes(title='', visible=False, showticklabels=True)
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), title='',
                          width=1000, height=600, font=dict(size=18))
        fig.write_image(dir_path + base_name + '.png')


display_names = {
    'steel_dri': 'Stahl DRI',
    'cement': 'Zement',
    'other industries': 'Andere',
    'glass_and_cermaics': 'Glass',
    'basic_chemicals': 'Grundstoff-Chemie',
    'Effective CO2 Price': 'CO2-Preis (effektiv)',
    'Industry': 'Sektor',
    'Project name': 'Projekt',
    'compare_sectors': 'Sektorvergleich',
    'Glass_0.3MT_2028a)': 'Glass (Bsp.)',
    'HD-Zement a)': 'HD-Zement',
    'Ammonia_0.3Mt_2025': 'Ammoniak (Bsp.)',
    'Abatement_cost': 'Vermeidungskosten',
    'steel_IPCEI': 'Stahl IPCEI',
    'Additional OPEX': 'Sonstige OPEX',
    'CAPEX annuity': 'CAPEX Annuität',
    'h2share_influence': 'Einfluss des H2-Anteils',
    'all': 'kombiniert',
    'h2': 'H2',
    'ng': 'Erdgas',
    'elec': 'Strom',
    'lowh2': '10-30% H2',
    'varyh2': '0-100% H2',
    'onlyh2': '100% H2',
    'prices': 'Preisannahmen',
    'Hydrogen': 'Wasserstoff',
    'Natural Gas': 'Erdgas',
    'Electricity': 'Strom',
    'Iron Ore': 'Eisenerz',
    'Injection Coal': 'Einblaskohle',
    'Scrap Steel': 'Stahlschrott',
    'Coking Coal': 'Kokskohle',
    'H2 Share': 'Anteil Wasserstoff',
    '': '',
    '': ''
}


def display_name(varname: str):
    if str(varname).startswith('sensitivity'):
        _, scen_name, h2name = varname.split('_')
        return f"Preisunsicherheit {display_name(scen_name)}, {display_name(h2name)}"
    else:
        return display_names.get(varname, varname)
