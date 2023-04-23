from src.setup.setup import Setup


def auction():
    pass


def calc_score():
    pass


def set_projects_current(setup: Setup, all_chosen_projects: list, config_ar: dict):
    setup.projects_current = setup.projects_all[
        ~setup.projects_all['Project name'].isin(all_chosen_projects)] \
        .query(f"`Time of investment` - 3 <= {config_ar['year']}")
    setup.projects_current['Time of investment'] = config_ar['year'] + 3
    return
