# import time
from src.setup.setup import Setup
from src.setup.select_scenario_data import select_scenario_data, select_h2share
from src.calc_costs.calc_cost_and_emissions import calc_cost_and_emissions
from src.calc_costs.calc_ccfd import calc_ccfd, calc_strike_price
import src.tools.gaussian as gs
from src.tools.tools import log


def run(config_filepath: str = None, config: dict = None):

    # st = time.time()

    setup = Setup(config_filepath, config)

    mode = setup.config['mode']
    if mode == 'auction':
        run_auction(setup)
        return
    elif mode == 'analyze_cost':
        cost_and_em = run_analyze(setup)
        return setup.config, setup.projects_all, cost_and_em


def run_auction(setup: Setup):

    for config_ar in setup.config['auction_rounds']:

        log(f"Enter auction round {config_ar['name']}...")

        projects_ar = setup.projects_all.query(f"`Time of investment` - 3 <= {config_ar['year']}")

        scenarios_bidding = select_scenario_data(
            data_raw=setup.scendata_raw,
            scenarios=setup.config['scenarios_bidding']
        )
        h2share = select_h2share(
            h2share_raw=setup.h2share_raw,
            projects=projects_ar,
            auction_year=config_ar['year']
        )

        cost_and_em_bidding = calc_cost_and_emissions(setup, scenarios_bidding, h2share,
                                                      projects_ar)
        strike_price = calc_strike_price(cost_and_em_bidding, projects_ar)
        cost_and_em_bidding, total_em_savings_bidding = calc_ccfd(cost_and_em_bidding, projects_ar,
                                                                  setup.techdata)

    # TODO:
    # calc_lcop() # sum(opex)/duration + capex / auslastungsfaktor
    # calc_abatement_cost() # npv( lcop_t - lcop_ref ) / npv( e_t - e_ref ), all per t of product
    # calc_strike_price()
    # calc_eff_co2_price()
    # calc_total_emission_saving()
    # calc_cap()

    return strike_price, total_em_savings_bidding  # linter only


def run_analyze(setup: Setup):

    scenarios = select_scenario_data(
        data_raw=setup.scendata_raw,
        scenarios=setup.config['scenarios_actual'],
        relative_standard_deviation=setup.config.get('relative_standard_deviation', None),
        absolute_standard_deviation=setup.config.get('absolute_standard_deviation', None)
    )
    h2share = select_h2share(
        h2share_raw=setup.h2share_raw,
        projects=setup.projects_all
    )

    cost_and_em = calc_cost_and_emissions(setup, scenarios, h2share, keep_components=True)
    strike_price = calc_strike_price(cost_and_em, setup.projects_all)
    cost_and_em, total_em_savings = calc_ccfd(cost_and_em, setup.projects_all, setup.techdata)

    cost_and_em = gs.get_bounds(cost_and_em)

    if False:
        print(strike_price, total_em_savings)

    return cost_and_em


if __name__ == '__main__':
    config_filepath = 'config/config_all.yml'
    strike_price = run(config_filepath)
    print(strike_price)
