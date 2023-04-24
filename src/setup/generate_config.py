from src.setup.select_scenario_data import read_all_scenario_data
import pandas as pd
import os
import yaml

all_components = ["Free Allocations",
      "Prices CO2",
      "Prices Natural Gas",
      "Prices Electricity",
      "Prices Hydrogen",
      "Prices Coking Coal",
      "Prices Injection Coal",
      "Prices Iron Ore",
      "Prices Scrap Steel",
      "Prices DRI-Pellets",
      "Prices Naphta" ]

selected_scenarios = dict([(c, "") for c in all_components])

class SingleQuoted(str):
    pass

def single_quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style="'")

yaml.add_representer(SingleQuoted, single_quoted_presenter)

def generate_config(scenario_dir: str, yaml_dir:str):
    stream = open(os.path.join(yaml_dir, 'config.yml'), 'w')
    final_dict = {
        'scenarios_dir': SingleQuoted(scenario_dir),
        'scenarios_actual': selected_scenarios,
        'scenarios_bidding': selected_scenarios
    }

    for key, value in final_dict.items():
        if isinstance(value, dict):
            stream.write(key + ":\n")
            for key_, value_ in value.items():
                stream.write("  ")
                stream.write(key_ + ":\n")
                if value_:
                    selected_scenario = value_
                else:
                    selected_scenario = read_all_component_scenarios(key_, scenario_dir)["Scenario"].iloc[0]

                stream.write("    '"+selected_scenario+"'\n")
                for scenario in read_all_component_scenarios(key_, scenario_dir)["Scenario"].values:
                    if scenario != selected_scenario:
                        stream.write("    #'"+scenario+"'\n")
        else:
            stream.write(yaml.dump({key: value}, default_flow_style=False))

def read_all_component_scenarios(component:str, scenario_dir: str):
    all_scenarios, h2share = read_all_scenario_data(dirpath=scenario_dir)

    if component.startswith('Prices '):
        return (all_scenarios.prices.query(f"Component=='{component.replace('Prices ', '')}'")
              .filter(items=['Scenario'])
              .drop_duplicates())
    else:
        return all_scenarios.free_allocations.filter(items=['Scenario']).drop_duplicates()

def read_all_by_columns(scenario_dir: str, groupByColumn:str, valueColumn:str):
    all_scenarios, h2share = read_all_scenario_data(dirpath=scenario_dir)

    prices = pd.concat([
            all_scenarios.prices.query(f"{groupByColumn}=='{component.replace('Prices ', '')}'")
            .filter(items=[groupByColumn,valueColumn])
            .drop_duplicates()
            for component in all_components if component.startswith("Prices ")
        ])
    free_allocations = all_scenarios.free_allocations.filter(items=[valueColumn]).drop_duplicates()
    free_allocations[groupByColumn] = "Free Allocations"
    all_scenarios = pd.concat([prices, free_allocations])
    return all_scenarios

def read_all_scenarios(scenario_dir: str):
    return read_all_by_columns(scenario_dir,'Component', 'Scenario')

def read_all_technologies(scenario_dir: str):
    return read_all_by_columns(scenario_dir,'Component', 'Technology')

def select_scenario(component:str, scenario:str, scenario_dir: str):
    all_scenarios = read_all_scenarios(scenario_dir)
    if scenario in all_scenarios.query(f"Component=='{component.replace('Prices ', '')}'")[["Scenario"]].values:
        selected_scenarios[component] = SingleQuoted(scenario)

def select_default_scenario(component:str, scenario_dir: str):
    all_scenarios = read_all_scenarios(scenario_dir)
    component_scenarios = all_scenarios.query(f"Component=='{component.replace('Prices ', '')}'")
    if(not component_scenarios.empty):
        default_scenario = component_scenarios["Scenario"].iloc[0]
        selected_scenarios[component] = SingleQuoted(default_scenario)

# activate default scenario for a specific component
# select_default_scenario("Free Allocations", 'data/scenarios/isi/')

# select a scenario for a specific component
# select_scenario("Prices CO2", "ETS-Preis hoch", 'data/scenarios/isi/')

# get list of all possible scenarios for a specific component as a pandas dataframe
# read_all_component_scenarios("Prices CO2", 'data/scenarios/isi/')

# generate the config file
# generate_config('data/scenarios/isi/','config/')
