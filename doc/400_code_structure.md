# Code Structure

The main routine is called `run` and is located in the file `run.py` in the main directory of the source code `cacoca`. A minimal example of how to use this routine in `auction` mode is located in the file `cacoca.py`. Examples of how to use it in `analyze_cost` mode in combination with subsequent plotting routines are given in `plot_slides.py`. CaCoCa is based on Python `pandas`, and the predominant data structure are `pandas DataFrames`

A cacoca run consists of three basic steps:

1. The setup is calculated. This includes reading in the configuration (general parameters and project definitions), reading in raw data (`tech` data, i.e. technology-specific demands, costs and emissions, as well as `scenario` data, i.e. for energy and feedstock price trajectories) and selecting raw data according to the chosen scenarios and project specifics. The setup is fully contained in an instance of a dedicated `Setup` class. All routines belonging to parameter and data read-in and setup are located in the `cacoca/setup` folder.
2. Calculating cost and emissions. This step includes calculations for several technologies and operation modes, and the subsequent combination of those. On the one hand, cost and emissions for a reference technology are always calculated alongside those for the transformative project. All calculated quantities for the reference are given the suffix `_ref`. The difference to the transformative project is then calculated for all quantities, and given the suffix `_diff`. But quantities for the transformative project are also calculated twice, for two different operation modes called `old` and `new`. This allows phasing in of new technologies or new fuel mixes over time via the time-dependent scenario parameter `H2 Share`. In particular, `H2 Share` is used for two different kinds of phasing in: For steel, the `old` fuel mix refers to direct reduction using natural gas, while `new` refers to direct reduction with hydrogen. This allows a gradual switch from natural gas to hydrogen. For cement, `old` is identical to the fossil reference technology, while only `new` refers to the CCS project. This allows modeling a gradual phase-in of CCS.
3. Calculating derived quantities from cost and emissions ( and their differences), such as abatement costs. In `auction` mode, quantities only needed for the auction (the auction score and a budget cap) are also calculated. All routines concerned with performing calculations are located in the `cacoca/calc` folder.

In `analyze_cost` mode, the three above steps are run only once. In `auction` mode, they are calculated twice per auction round: Once before the auction using the `bidding` price scenarios given in the config file, on the basis of which the auction is then carried out. And once after the auction with only the projects chosen in that auction round and the `actual` price scenarios given in the config file, to calculate the eventual payout the projects receive.

The auction itself is currently purely price-based, i.e. projects calculate their strike price based on the abatement cost. Projects are then sorted by an auction score calculated according to the criteria in the german tender document in its mid-2023 state. The budget cap is calculated for each project, and the $n$ highest scoring projects are chosen, such that the summed budget caps are just below the budget of the auction round.
In each auction round, the projects entering the auction is updated: First, only projects with `Time of investment` within three years of the auction year take part (this is a requirement in the tender). Second, projects successful in previous rounds do not take part in the following ones.

The `run` function returns a data frame which can be used as input to several plotting routines, which are located in the `cacoca/output`. Currently, only plotting routines for the output of runs in the `analyze_cost` mode are implemented.

## Sensitivities

CaCoCa allows to calculate and display upper and lower bounds due to uncertain input parameters (currently only uncertain prices are implemented, but other uncertainties such as in energy demands can be added easily).

A use example is contained in the file `plot_slides.py`, where the parameters under `relative_uncertainty` are added to the config dictionary to plot uncertainty bounds.

To implement this, the function decorator `@with_sensitivities` is defined in the file `cacoca/tools/sensitivities.py`. If you are not familiar with the concept of Python function decorators, please refer to a tutorial of your choice. Any function calculating output quantities from input prices can be decorated to obtain the bounds in addition to the mean values.

The implementation assumes all uncertain input parameters $p_i,\;\;i=1,...,N$ to have a normal (Gaussian) distribution with expectation $\mu_{p_i}$ and standard deviation $\sigma_{p_i}$. The current implementation takes advantage of the fact that all output quantities of interest $q$ are linear functions of all $p_i$, such that $q(p_i)$ is of the form

$q(p_i) = a + \sum_i b_i \, p_i.$

where the derivatives

$\frac{\partial q}{\partial p_i} = b_i$

This entails that the expectation of the output $\mu_q$ is

$\mu_q = q(\mu_{p_i}) = a + \sum_i b_i \, \mu_{p_i}$

and its variance (i.e. squared standard deviation) $\sigma_q^2$ is

$\sigma_q^2 = \sum_i (b_i \, \sigma_{p_i})^2.$

The standard deviations of the prices $\sigma_{p_i}$ are given as input parameters in the yml file. The trajectories normally given for these prices are taken as their expected values $\mu_{p_i}$. The implementation of the function decorator (more specifically, of the function wrapper) then follows the following steps:

- compute the baseline $\mu_q$ using the expected values of the prices $\mu_q = q(\mu_{p_i})$
- compute the derivatives w.r.t. each uncertain price (i.e. the coefficients $b_i$, as was shown above) from a finite difference, where the price is disturbed by $1$. This is exact due to the linearity of $q(p_i)$. The coefficients are thus computed as $b_i = \frac{\partial q}{\partial p_i} = \frac{q(p_i+1)-q(p_i)}{1}$.
- multiply these coefficients with the input standard deviations $\sigma_{p_i}$ and sum them to obtain the total output variance $\sigma_q^2$.
- The upper and lower bounds of a 95 % confidence interval $\mu_q \pm 2\,\sigma_q$ are computed and given the suffixes `_upper` and `_lower`, respectively.

## Getting to know the code

In order to get to know the source code more closely, we recommend stepping through it with a debugger and following the changes made to the data frames in each line or section.
