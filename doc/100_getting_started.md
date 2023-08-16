# Installation

For Windows installation, all given commands have to be executed in PowerShell
(NOT in commandline, that is a different shell and will lead to errors!)

Note that for paths in commands, Linux path separators (`/`) are mostly given. Windows PowerShell mostly recognizes that, ut in some instances you might have to change that to the Windows separator `\`.

## Clone Cacoca

Make sure that you have git installed, have generated a public ssh key and added it to your github account.

Clone the repository using `git clone git@github.com:JakobBD/cacoca.git` from the parent directory of your choice.

## Install Python 3.10.10

We have defined to use this exact version of python. You can download it from [https://www.python.org/downloads/release/python-31010/](https://www.python.org/downloads/release/python-31010/)

### Windows

In the above link, download the `Windows installer (64-bit)`. For me this meant to uninstall another Python3.10 version first, but there may be other ways.

### Ubuntu

You can have several python versions in parallel using `pyenv`.

## Install Poetry

Poetry manages Python and library versions.

For installation, follow the instructions on the website: [https://python-poetry.org/docs/](https://python-poetry.org/docs/)

You might have to at the binary path to your PATH environment variable.

Installation was successful if the command `poetry --version` prints the version number.

## Install dependencies

From the cacoca repository, run

```
poetry install
```

This should install all the required packages.

## Add cacoca directory to PYTHONPATH environment variable

Right now, Python will not find the cacoca package, so we have to tell Python where to look for it by adding the directory the the PYTHONPATH environment variable.

### Windows

In the Windows start menu, search again for `edit environment variables for your account`.

- If select `PYTHONPATH` already appears in the upper window:
Press `Edit...`, then press `New` and add the location of the cacoca repository. Press OK twice.
- If it doesn't_ Press `New`, enter `PYTHONPATH` under variable name, and the cacoca repository path as variable value. Again, press OK twice.

This might need a system restart.

### Ubuntu

Add the line
```
export PYTHONPATH=$PYTHONPATH:/MY/CACOCA/EXAMPLE/PATH
```
(with an adapted path) to your `~/.bashrc` and save it. Re-open the terminal.

## Windows: Fix Kaleido Bug

I encountered a bug with the kaleido package needed for saving plotly figures as png under Windows (to reproduce the error, run the command given in the 'Test Run (Analysis/Plotting)' section): It complained that it couldn't find the kaleido executable. I solved this by looking for the site packages directory by changing to the `cacoca` repo and from there running
```
poetry run python -m site
```
This will list several directories, of which I selected one that's called
```
C:\\Users\\username\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\cacoca-...-py3.10\\lib\\site-packages
```
(can be different on your machine) and from there I opened the file
```
kaleido\scopes\base.py
```
In line 75, I changed `kaleido` to `kaleido.cmd`.  This solved the bug for me.

# Test Run

## Auction Mode

From the `cacoca` repository, run

```
poetry run python ./cacoca.py ./config/config.yml
```

This should create some lines of stdout for the different auction rounds.

## Analysis/Plotting Mode

From the `cacoca` repository, run

```
poetry run python ./plot_slides.py
```

This should create some png files in the `output` directory and it should open browser tabs with the figures.

Alternatively, you can run this command in your IDE. Make sure to select the cacoca poetry virtual environment as the interpreter.

In VSCode, executing `plot_slides.py` in interactive mode (using the Jupyter extension) also shows you the `plotly` figures in an interactive output, if you set `show_figs_in_browser: False` in the file `config/config_slides.yml`. This may not work in other IDEs like PyCharm, but the browser should be fine as an alternative.

