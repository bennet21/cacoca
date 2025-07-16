# CaCoCa

CaCoCa (The Carbon Contracts Calculator) is a tool to model carbon contracts for difference (CCfDs) for industrial decarbonization projects. Abatement cost time curves can be calculated, and auctions of such carbon contracts (where the projects bidding the lowest carbon price are awarded contracts) can be modeled.

The techno-economic input data provided in this repository is incomplete and not to be relied upon. It only serves as an example for the functionality of the code. It is advised to use your own data.

## Installation

The Python version and packages are managed using [PEP 621](https://peps.python.org/pep-0621/). Packages are listed in the file [pyproject.toml](pyproject.toml). Detailed instructions for installation can be found in the [documentation](doc/100_getting_started.md).

## Quick start / basic run

Runs are configured using a YAML input file. Example input files are located in the `config` folder.

For a test run, go to the main directory and run

```
poetry run python cacoca.py config/config.yml
```

This should create some lines of stdout for the different auction rounds.

## Contributors

The authors of CaCoCa are:

Jakob Dürrwächter\
Robin Blömer\
Philipp Verpoort\
Paul Effing\
Johannes Eckstein\
Falko Ueckerdt

## License

CaCoCa is Copyright (C) 2023, Jakob Dürrwächter, Robin Blömer, Johannes Eckstein and Falko Ueckerdt and is released under the terms of the
GNU General Public License v3.0. For the full license terms see
the included [`LICENSE` file](LICENSE).

## Reference / Please cite

To cite CaCoCa, please use:

J. Dürrwächter, R.Blömer, P. Verpoort, P. Effing, J. Eckstein, F. Ueckerdt (2023). _CaCoCa: The Carbon Contracts Calculator._ Version 0.1.0, <https://github.com/JakobBD/cacoca>.

A BibTeX entry for LaTeX users is:

 ```latex
@Manual{,
  title = {CaCoCa: The Carbon Contracts Calculator},
  author = {Jakob Dürrwächter and Robin Blömer and Philipp Verpoort and Paul Effing and Johannes Eckstein and Falko Ueckerdt},
  year = {2023},
  note = {Version 0.1.0},
  url = {https://github.com/JakobBD/cacoca},
}
```

## Documentation

Further documentation can be found in the [`doc/` folder](doc/).


