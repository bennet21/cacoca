# %%
import plotly as pl
import pandas as pd
from src.input.read_scenario_data import read_all_scenario_data, years_to_rows, add_variance
from src.output.plot_project_cost_time_curves import plot_project
from src.output.plot_tools import add_color, show_and_save
from src.tools.gaussian import get_bounds


def plot_price_scenarios(config: dict, projects: pd.DataFrame, project_names: list,
                         do_emphasize: bool = True):

    print_other = True

    scen_dir_path = config['scenarios_dir']
    config = config["scenarios_actual"]

    data_all, h2share = read_all_scenario_data(dirpath=scen_dir_path)

    prices = years_to_rows(
        data_all.prices, year_name="Period", value_name="Price"
    )
    prices = prices.drop(columns='Source Reference')

    # Hack to make it fit in price plotting scheme below
    h2share = years_to_rows(h2share, year_name="Period", value_name="Price")

    for project_name in project_names:
        h2share_scen = projects \
            .query(f"`Project name` == '{project_name}'")["H2 Share Scenario"] \
            .values[0]
        config["Prices H2 Share " + project_name] = h2share_scen
        h2share["Component"] = "H2 Share " + project_name
        h2share["Unit"] = "H2 Share"
        prices = pd.concat([prices, h2share])

    add_variance(prices, mode='h2_and_co2_sigma0.2')
    prices = get_bounds(prices)

    for component_name, cdf in prices.groupby('Component'):

        fig = pl.graph_objs.Figure()

        cdf = add_color(
            cdf,
            by_column='Scenario'
        )

        for scenario_name, sdf in cdf.groupby('Scenario'):
            color = sdf['color'].values[0]
            legend_name = scenario_name

            if do_emphasize and "Prices " + component_name in config:
                if config["Prices " + component_name] == scenario_name:
                    emphasize = 'main'
                else:
                    emphasize = 'other'
                    if not print_other:
                        continue
            else:
                emphasize = None

            plot_project(fig,
                         sdf,
                         vname='Price',
                         legend_name=legend_name,
                         hovername=scenario_name,
                         color=color,
                         emphasize=emphasize)

        fig.update_layout(legend=dict(title='Szenario'),
                          title=component_name)
        fig.update_xaxes(title='Jahr')
        fig.update_yaxes(title=sdf['Unit'].values[0])
        show_and_save(fig, 'prices_' + component_name)

        # %%
