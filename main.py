# %%
import time
from src.input.read_config import read_config
from src.input.read_projects import read_projects
from src.input.read_techdata import read_techdata
from src.input.read_scenario_data import read_scenario_data
from src.calc_costs.calc_cost_and_emissions import calc_cost_and_emissions
from src.calc_costs.calc_ccfd import calc_ccfd, calc_strike_price
from src.output.plot_project_cost_time_curves import plot_project_cost_time_curves
from src.output.plot_stacked_bars import plot_stacked_bars
from src.output.plot_price_scenarios import plot_price_scenarios
import src.tools.gaussian as gs
from config.project_list_ALL import project_names


# import sys
# config_filepath = sys.argv[1]
config_filepath = 'config/config_all.yml'
# config_filepath = 'config/config.yml'

st = time.time()

config = read_config(config_filepath)

projects = read_projects(
    config['projects_file'],
    config['default_wacc']
)

techdata, reference_tech = read_techdata(
    config['techdata_dir'],
    config['techdata_files']
)

# techdata = expand_by_years(techdata,
#                            config['years'])

scenarios_actual, scenarios_bidding, h2share = read_scenario_data(
    config['scenarios_dir'],
    config['scenarios_actual'],
    config['scenarios_bidding'],
    projects
)


cost_and_em_actual = calc_cost_and_emissions(projects, techdata, reference_tech,
                                             scenarios_actual, h2share, config)
cost_and_em_bidding = calc_cost_and_emissions(projects, techdata, reference_tech,
                                              scenarios_bidding, h2share, config)

strike_price = calc_strike_price(cost_and_em_bidding, projects)


cost_and_em_actual, total_em_savings_actual = calc_ccfd(cost_and_em_actual, projects, techdata)
cost_and_em_bidding, total_em_savings_bidding = calc_ccfd(cost_and_em_bidding, projects, techdata)

# calc_lcop() # sum(opex)/duration + capex / auslastungsfaktor
# calc_abatement_cost() # npv( lcop_t - lcop_ref ) / npv( e_t - e_ref ), all per t of product
# calc_strike_price()
# calc_eff_co2_price()
# calc_total_emission_saving()
# calc_cap()

et = time.time()
# print(et-st)

# %%

cost_and_em_actual = gs.get_bounds(cost_and_em_actual)

# glass_and_ceramics, other_industries, cement, steel_dri, basic_chemicals
sector = 'steel_dri'


plot_project_cost_time_curves(cost_and_em_actual, sector=sector, project_names=project_names,
                              print_name='steel_IPCEI')

for project_name in project_names:
    plot_stacked_bars(cost_and_em_actual, project_name=project_name)

plot_price_scenarios(config, projects, project_names)


print()

# %%
