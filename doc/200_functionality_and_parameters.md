# Functionality and Parameters

The basic principle of CaCoCa is to perform a number of calculations for a set of pre-defined proposed industrial decarbonization projects, which correspond to bidders in a CCfD tender. For each project, a technology can be specified, which is defined by CAPEX, OPEX, specific emissions and specific feedstock and energy demands. For each transformative green technology, a fossil reference technology is given. To calculate energy costs, energy price developments over time are assumed as inputs. They can be chosen from several scenarios.

The repository is structured as follows:
- The source code is located in the `cacoca` subdirectory
- General parameters are located in `yml` file in the `config` directory, projects definitions are in the `projects.csv` file in the same directory. They contain for each project data such as its name, used technology, planned production size, and so on.
- Technologies (CAPEX, OPEX, specific emissions and specific feedstock and energy demands) are defined in the `data/tech` subdirectory, in a `csv` file for each sector; Different sub-folders can be placed in this directory to choose from different data sources by changing the according path in the config file.
- Price trajectories are defined in the `data/secnarios` subdirectory; Different sub-folders can be placed in this directory to choose from different data sources by changing the according path in the config file.
- The `output` folder is where e.g. figures can be saved
- The `scripts` folder contains helper scripts which are not needed for cacoca execution itself.

CaCoCa can be run in two modes:
- In `auction` mode, several auction rounds are carried out, where a subset of projects is successful in each round. Currently, this mode yields a text output of successful projects, summed budget cap of the successful projects, and eventual payout. More detailed figure output can be added easily.
- In `analyze_cost` mode, quantities are calculated for each project, which can be plotted in various plotting routines.
Details on the implementation are given in the description of the code structure.

## Parameters in `config.yml`

| Parameter | Possible values | Description |
|-----------|-------------|-------------|
| `mode` | `auction` or `analyze_cost` | basic mode to run cacoca in, see mode descriptions above. |
| `techdata_dir` | directory path | directory path for techno-economic data |
| `techdata_files` | list of file names without extension | list of files to read technology data from |
| `projects_file` | file path | path to file defining projects which are considered in the cacoca run |
| `do_overwrite_project_start_year` | `True` or `False` | overwrite the values given in the projects definition; This can be useful for plotting in earlier years |
| `project_start_year_overwrite` | calendar year | year to overwrite the values from the projects definition with if `do_overwrite_project_start_year = True` |
| `start_year` | calendar year | Earliest calendar year considered in the cacoca run |
| `end_year` | calendar year | Latest calendar year considered in the cacoca run |
| `ccfd_duration` | duration in years |  |
| `default_wacc` | float; e.g. `0.06` |  |
| `show_figures` | `True` or `False` | Show figures in interactive mode (can be turned off to accelerate a run if figures are only to be saved) |
| `show_figs_in_browser` | `True` or `False` | If true, a tab is opened for each figure in the default browser; if False, the current IDE is used, if it has such capabilities, such as VSCode's a Jupyter notebook extension |
| `output_dir` | directory path | main directory of the figure output, relative to directory the run was started from |
| `save_figures` | `True` or `False`False | whether or not to save figures |
| `crop_figures` | `True` or `False`True | whether or not to remove the title from figures and have a tighter outer bound; useful for integration in Powerpoint |
| `scenarios_dir` | directory path | directory path for scenario definition, such as energy carrier price trajectories |
| `scenarios_actual` | contains the sub-parameters `free_allocations` and `prices` | (price) scenarios of actually occurring prices, which are used to calculate the actual eventual payout to projects. |
| `  free_allocations` | name of a free allocation trajectory scenario defined in the file `data/scenarios/` ... `/free_allocations.csv` | Free emission allocation scenarios under the EU ETS |
| `  prices` | contains sub-parameters for each price trajectory | price trajectories for energy carriers, feedstocks and CO2; currently, those are `Electricity`, `CO2`, `Natural Gas`, `Hydrogen`, `Coking Coal`, `Injection Coal`, `Iron Ore`, `Scrap Steel`, `DRI-Pellets` and `Naphta`. For each of these inputs, the name of a price trajectory scenario defined in the `data/scenarios` directory is given. |
| `scenarios_bidding` | same structure as `scenarios_actual` | Scenarios forming the basis for the strike price calculation. Only used in `auction` mode. |
| `auction_round_default` | contains sub-parameters | sub-dictionary of parameters which are used as a default for every auction round; can be overwritten by the ones in `auction_rounds` |
| `  budget_cap_co2_price_scen` | CO2 price scenario name | lower bound CO2 price scenario used for budget cap calculation |
| `  budget_cap_alpha` | float, e.g. `0.2` | Specific for German tender design; "Faktor zur Bestimmung der maximierten Dynamisierungskomponente"; Maximum cost increase in energy carriers used in budget cap calculation. |
| `  strike_price_a` |  float, e.g. `0.5` | Specific for German tender design; "Gewichtungsfaktor a"; Weighting of relation to sector-specific maximum strike price used in auction score calculation. |
| `  rel_em_red_rr` |  float, e.g. `0.5` | Specific for German tender design; "Vergleichswert für die relative Treibhausgasemissionsminderung"; reference value for relative emission reduction used in auction score calculation. |
| `  rel_em_red_s` |  float, e.g. `0.2` | Specific for German tender design; "Gewichtungsfaktor für die relative Treibhausgasemissionsminderung"; weighting factor for relative emission reduction used in auction score calculation. |
| `auction_rounds` | contains list of sub-directories with sub-parameters | list of auction rounds, each consisting of a sub-dictionary of parameters which complement or overwrite the default ones for this auction round; i.e. all the parameters introduced above as sub-parameters of `auction_round_default` can be added here to set them individually for an auction round; Some others following below only make sense if set individually |
| `  name` | arbitrary string | name of the auction round |
| `  year` | calendar year (integer) | year the auction takes place |
| `  budget_BnEUR` | float | budget (for summed budget caps of all successful projects) in billion € for this auction round |