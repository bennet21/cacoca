import plotly as pl
import pandas as pd
import os


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


def show_and_save(fig: pl.graph_objs.Figure, config: dict, base_name: str = None):
    if config['show_figures']:
        if config['show_figs_in_browser']:
            pl.io.renderers.default = "browser"
        fig.show()
    if base_name and config['save_figures']:
        dir_path = config['output_dir']
        if config['crop_figures']:
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), title='')
        fig.update_layout(width=1000, height=600, font=dict(size=18))
        fig.write_image(os.path.join(dir_path, base_name + '.png'))


display_names = {
    'steel_dri': 'Stahl DRI',
    'cement': 'Zement',
    'other_industries': 'Andere',
    'glass_and_ceramics': 'Glass',
    'basic_chemicals': 'Grundstoff-Chemie',
    'Effective CO2 Price': 'Effective CO2 Price',
    'Industry': 'Sector',
    'Project name': 'Project Name',
    'compare_sectors': 'Sector comparison',
    'Abatement_cost': 'Abatement_cost',
    'Additional OPEX': 'Additional OPEX',
    'CAPEX annuity': 'CAPEX annuity',
    'h2share_influence': 'Einfluss des H2-Anteils',
    'ccsshare_influence': 'Einfluss des CCS-Anteils',
    'all': 'combined',
    'h2': 'H2',
    'ng': 'Natural Gas',
    'elec': 'Electricity',
    'ccoal': 'Coking Coal',
    'lowh2': '10-30% H2',
    'varyh2': '0-100% H2',
    'onlyh2': '100% H2',
    'prices': 'Prices',
    'Hydrogen': 'Hydrogen',
    'Natural Gas': 'Natural Gas',
    'Electricity': 'Electricity',
    'Iron Ore': 'Iron Ore',
    'Injection Coal': 'Injection Coal',
    'Scrap Steel': 'Steel Scrap',
    'Coking Coal': 'Coking Coal',
    'H2 Share': 'H2 Share',
    'all_projects': 'All Projects',
    'CO2 Cost': 'CO2 Costs',
    'Biomass': 'Biomass',
    'DRI-Pellets': 'DRI-Pellets',
}


def display_name(varname: str):
    if str(varname).startswith('sensitivity'):
        _, scen_name, h2name = varname.split('_')
        return f"Preisunsicherheit {display_name(scen_name)}, {display_name(h2name)}"
    else:
        return display_names.get(varname, varname)


def to_rgba(color: str, alpha: float):
    if isinstance(color, tuple):
        rgba = f"rgba{color + (alpha,)}"
    elif color.startswith("#"):
        rgba = f"rgba{pl.colors.hex_to_rgb(color) + (alpha,)}"
    else:
        rgba = color.replace("rgb", "rgba").replace(")", f", {alpha})")
    return rgba


def change_output_subdir_by_filename(config: dict, filename):
    subdirname = os.path.basename(filename)
    subdirname = os.path.splitext(subdirname)[0]
    if subdirname == os.path.split(config['output_dir'])[1]:
        return
    subdir = os.path.join(config['output_dir'], subdirname)
    if not os.path.exists(subdir):
        os.makedirs(subdir)
    config['output_dir'] = subdir
    return
