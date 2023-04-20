from src.setup.setup import Setup
from src.calc_costs.calc_cost_and_emissions import calc_cost_and_emissions
from src.calc_costs.calc_ccfd import calc_ccfd, calc_strike_price, calc_budget_cap
# from tools.sensitivities import
from src.tools.tools import log


def run(config_filepath: str = None, config: dict = None):

    setup = Setup(config_filepath, config)

    mode = setup.config['mode']
    if mode == 'auction':
        run_auction(setup)
        return
    elif mode == 'analyze_cost':
        cost_and_em = run_analyze(setup)
        return setup.config, setup.projects_all, cost_and_em


def run_auction(setup: Setup):

    all_chosen_projects = {}

    for config_ar in setup.config['auction_rounds']:

        log(f"Enter auction round {config_ar['name']}...")

        projects_ar = setup.projects_all[
            ~setup.projects_all['Project name'].isin(all_chosen_projects)] \
            .query(f"`Time of investment` - 3 <= {config_ar['year']}")

        setup.select_scenario_data('scenarios_bidding')
        setup.select_h2share(projects=projects_ar,
                             auction_year=config_ar['year'])

        cost_and_em_bidding = calc_cost_and_emissions(setup, projects_ar)
        strike_price = calc_strike_price(cost_and_em_bidding, projects_ar)
        cost_and_em_bidding, total_em_savings_bidding = \
            calc_ccfd(cost_and_em_bidding, projects_ar, setup.techdata)

        cost_and_em_bidding, cap_sum = calc_budget_cap(cost_and_em_bidding, strike_price, setup)

        # TODO:
        # calc_cap()
        # chosen_projects = auction() # chosen_projects includes column with auction round name
        # calc_payout(chosen_projects)
        # all_chosen_projects += chosen projects
        # return all_chosen_projects

    return strike_price, total_em_savings_bidding  # linter only


def run_analyze(setup: Setup):

    setup.select_scenario_data(scenarios='scenarios_actual')
    setup.select_h2share()

    cost_and_em = calc_cost_and_emissions(setup, keep_components=True)
    strike_price = calc_strike_price(cost_and_em, setup.projects_all)
    cost_and_em, total_em_savings = calc_ccfd(cost_and_em, setup.projects_all, setup.techdata)

    if False:
        print(strike_price, total_em_savings)

    return cost_and_em


if __name__ == '__main__':
    config_filepath = 'config/config_all.yml'
    strike_price = run(config_filepath)
    print(strike_price)
