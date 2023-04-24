import pandas as pd
from src.setup.setup import Setup
from src.tools.tools import log


def auction(aggregate: pd.DataFrame, setup: Setup, config_ar: dict):
    aggregate = aggregate.sort_values('score', ascending=False)
    aggregate['budget_cumsum'] = aggregate['budget_cap'].cumsum()

    chosen_projects = aggregate[aggregate['budget_cumsum'] <= config_ar['budget_BnEUR'] * 1000.]

    chosen_proj_list = chosen_projects['Project name'].values.tolist()
    n_chosen_proj = chosen_projects.shape[0]
    log(f"  {n_chosen_proj} projetcs chosen")
    log("    " + " | ".join(chosen_proj_list))
    spent_budget = chosen_projects['budget_cumsum'].iloc[-1] / 1000. if n_chosen_proj else 0.
    log(f"  Budget cap: {spent_budget:0.3f} Bn € "
        + f"of {config_ar['budget_BnEUR']} Bn €")

    return chosen_proj_list


def prepare_setup_for_bidding(setup: Setup, all_chosen_projects: list, config_ar: dict):
    set_projects_ar(setup, all_chosen_projects, config_ar)
    setup.select_scenario_data('scenarios_bidding')
    setup.select_h2share(auction_year=config_ar['year'])
    return


def prepare_setup_for_payout(setup: Setup, chosen_projects: list, config_ar: dict):
    setup.projects_current \
        = setup.projects_all[setup.projects_all['Project name'].isin(chosen_projects)].copy()
    setup.projects_current['Time of investment'] = config_ar['year'] + 3
    setup.select_scenario_data(scenarios='scenarios_actual')
    setup.select_h2share(auction_year=config_ar['year'])
    return


def set_projects_ar(setup: Setup, all_chosen_projects: list, config_ar: dict):
    setup.projects_current = setup.projects_all[
        ~setup.projects_all['Project name'].isin(all_chosen_projects)] \
        .query(f"`Time of investment` - 3 <= {config_ar['year']}")
    setup.projects_current['Time of investment'] = config_ar['year'] + 3
    return
