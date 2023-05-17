import plotly as pl
import pandas as pd
from ..setup.read_input import read_raw_scenario_data
from ..setup.select_scenario_data import years_to_rows
from .plot_project_cost_time_curves import plot_project
from .plot_tools import add_color, show_and_save, set_yrange_min_zero
from .plot_tools import display_name as dn
# from tools.sensitivities import sensitivity_to_bounds


def plot_price_scenarios(config: dict, projects: pd.DataFrame, project_names_h2share: list,
                         do_emphasize: bool = True):

    print_other = True

    scen_dir_path = config['scenarios_dir']

    prices_raw, _, h2share_raw = read_raw_scenario_data(dirpath=scen_dir_path)

    prices = years_to_rows(prices_raw, year_name="Period", value_name="Price")
    prices = prices.drop(columns='Source Reference')

    if project_names_h2share is not None:
        # Hack to make it fit in price plotting scheme below
        h2share = years_to_rows(h2share_raw, year_name="Period", value_name="Price")

        h2share_scens = []
        for project_name in project_names_h2share:
            h2share_scen = projects \
                .query(f"`Project name` == '{project_name}'")["H2 Share Scenario"] \
                .values[0]
            h2share_scens.append(h2share_scen)

        h2share["Component"] = "H2 Share"
        h2share["Unit"] = "H2 Share"
        prices = pd.concat([prices, h2share])

    for component_name, cdf in prices.groupby('Component'):

        fig = pl.graph_objs.Figure()

        cdf = add_color(
            cdf,
            by_column='Scenario'
        )

        for scenario_name, sdf in cdf.groupby('Scenario'):
            color = sdf['color'].values[0]
            legend_name = scenario_name

            if not do_emphasize:
                emphasize = 'all_equal'
            else:
                if component_name == 'H2 Share':
                    is_emphasized = scenario_name in h2share_scens
                else:
                    is_emphasized = \
                        config['scenarios_actual']['prices'][component_name] == scenario_name
                emphasize = 'main' if is_emphasized else 'other'

            if emphasize == 'other' and not print_other:
                continue

            plot_project(fig,
                         sdf,
                         vname='Price',
                         legend_name=legend_name,
                         hovername=scenario_name,
                         color=color,
                         emphasize=emphasize)

        fig.update_layout(legend=dict(title='Szenario'),
                          title=f"{dn('prices')} {dn(component_name)}")
        # fig.update_xaxes(title='Jahr')

        set_yrange_min_zero(fig)
        fig.update_yaxes(title=dn(sdf['Unit'].values[0]))

        show_and_save(fig, config, 'prices_' + component_name)
