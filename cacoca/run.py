from .setup.setup import Setup
from .calc.calc_cost_and_emissions import calc_cost_and_emissions
from .calc.calc_derived_quantities import calc_derived_quantities, calc_payout
from .calc.calc_auction_quantities import calc_auction_quantities
from .calc.auction import prepare_setup_for_bidding, auction, prepare_setup_for_payout
from .tools.sensitivities import with_sensitivities
from .tools.tools import log


def run(config_filepath: str = None, config: dict = None):

    setup = Setup(config_filepath, config)

    mode = setup.config['mode']
    if mode == 'auction':
        all_chosen_projects = run_auction(setup)
        return all_chosen_projects
    elif mode == 'analyze_cost':
        cost_and_em = run_analyze(setup)
        return setup.config, setup.projects_all, cost_and_em


def run_auction(setup: Setup):

    all_chosen_projects = []

    for config_ar_specific in setup.config['auction_rounds']:

        config_ar = setup.config['auction_round_default'] | config_ar_specific

        log(f"Enter auction round {config_ar['name']}...")

        prepare_setup_for_bidding(setup, all_chosen_projects, config_ar)

        cost_and_em_bidding = calc_cost_and_emissions(setup)
        yearly = calc_derived_quantities(cost_and_em_bidding, setup)
        yearly, aggregate = calc_auction_quantities(yearly, setup, config_ar)

        chosen_projects = auction(aggregate, setup, config_ar)
        all_chosen_projects += chosen_projects

        prepare_setup_for_payout(setup, chosen_projects, config_ar)
        cost_and_em_actual = calc_cost_and_emissions(setup)
        cost_and_em_actual = calc_derived_quantities(cost_and_em_actual, setup)
        p_yearly, p_aggregate, payout_ar = calc_payout(cost_and_em_actual, setup)
        log(f"  Payout: {payout_ar/1000.:0.3f} Bn €")
        log("")

        # TODO:
        # adjust size by Auslastungsfaktor where necessary
        # add plotting for payout, exclude negative payout projects

    return all_chosen_projects


def run_analyze(setup: Setup):

    setup.select_scenario_data(scenarios='scenarios_actual')
    setup.select_h2share()

    yearly = calc_analyze(setup)

    return yearly


@with_sensitivities
def calc_analyze(setup: Setup):
    cost_and_em = calc_cost_and_emissions(setup, keep_components=True)
    yearly = calc_derived_quantities(cost_and_em, setup)
    return yearly
