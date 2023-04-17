# import time
from src.input.read_config import read_config
from src.input.read_projects import read_projects
from src.input.read_techdata import read_techdata
from src.input.read_scenario_data import read_scenario_data
from src.calc_costs.calc_cost_and_emissions import calc_cost_and_emissions
from src.calc_costs.calc_ccfd import calc_ccfd, calc_strike_price
import src.tools.gaussian as gs


def run(config_filepath: str = None, config: dict = None):

    # st = time.time()
    if bool(config_filepath) == bool(config):
        raise Exception('Specify either config_filepath or config dict.')
    if bool(config_filepath):
        config = read_config(config_filepath)

    mode = config['mode']
    if mode not in ['analyze_cost', 'auction']:
        raise Exception('Invalid mode')

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
        dirpath=config['scenarios_dir'],
        projects=projects,
        scenarios_actual=config['scenarios_actual'],
        scenarios_bidding=config.get('scenarios_bidding', None),
        relative_standard_deviation=config.get('relative_standard_deviation', None),
        absolute_standard_deviation=config.get('absolute_standard_deviation', None)
    )

    keep_components = mode == 'analyze_cost'
    cost_and_em_actual = calc_cost_and_emissions(projects, techdata, reference_tech,
                                                 scenarios_actual, h2share, config,
                                                 keep_components)

    cost_and_em_actual, total_em_savings_actual = calc_ccfd(cost_and_em_actual, projects, techdata)

    if mode == 'auction':
        cost_and_em_bidding = calc_cost_and_emissions(projects, techdata, reference_tech,
                                                      scenarios_bidding, h2share, config)
        strike_price = calc_strike_price(cost_and_em_bidding, projects)
        cost_and_em_bidding, total_em_savings_bidding = calc_ccfd(cost_and_em_bidding, projects,
                                                                  techdata)

    # TODO:
    # calc_lcop() # sum(opex)/duration + capex / auslastungsfaktor
    # calc_abatement_cost() # npv( lcop_t - lcop_ref ) / npv( e_t - e_ref ), all per t of product
    # calc_strike_price()
    # calc_eff_co2_price()
    # calc_total_emission_saving()
    # calc_cap()

    if mode == 'analyze_cost':
        cost_and_em_actual = gs.get_bounds(cost_and_em_actual)

    # et = time.time()
    # print(et-st)
    if mode == 'analyze_cost':
        return config, projects, cost_and_em_actual
    elif mode == 'auction':
        # prvent linter errors by printing
        print(cost_and_em_actual, cost_and_em_bidding,
              total_em_savings_actual, total_em_savings_bidding,
              strike_price)
        return


if __name__ == '__main__':
    config_filepath = 'config/config_all.yml'
    config, projects, cost_and_em_actual = run(config_filepath)
