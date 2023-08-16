# Modifying Input Data

The config file `config\config_XY.yml` can currently only be modified with a text editor.

For `csv` files, there are several options. Text editors or other tools such as the VSCode `Edit csv` extension can be used, but don't offer the full capabilities of tools like Excel. Using Excels own csv loader and exporting to csv may lead to issues with string encoding. Therefore, a different tool was implemented in the file `scripts\input_viewer.xlsm`.

Currently, only part of its capabilities are functional: You can load single csv files into a new tab using the `Load Single...` button, edit them to your liking, and save them using the `Save Single` button. If you wish to save them under a new name, use `Save Single As...`.

The buttons on top are supposed to load and save all csv files at once. There is a bug in the functionality, so it is not explained in detail here.

<!-- It loads all the different `.csv` files needed for a cacoca run: The `config\projects_XY.csv`, the tech data located in `data\tech` and the scenario dat located in `data/scenarios` (loading `yml` files is not yet implemented). Select the paths for them (in the `cacoca_data` repo! The `cacoca` one only contains non-functional open-source data!) and hit `Load all`. You can now modify the data sheets. There should be drop down menus wherever you can select scenarios or technologies. After modification you can simply hit `Save all` and check your changes via `git diff HEAD`. If you wish, you can change the paths in the `Loader` sheets before hitting `Save all` to save the changes in a different place. Make sure to actually create these directories before you try to save files in them. And you have to adapt the according paths in the `config.yml`. -->

You don't have to save the `input_viewer.xlsm` file itself. Please only commit changes to this file to git if you have made changes to the VBA part of the file which are relevant to others. If you do so, please hit "clear all" before, so that the file gets uploaded without the imported sheets.

Unfortunately, the viewer is pretty rigid in which files to open. S oif you want to copy lines e.g. from one projects file to another, you can copy and paste the `input_viewer.xlsm` such that you can open it twice and then open the different projects files in the two instances. Alternatively, you can just copy the lines directly in the csv files with a text editor. Generally, the input_viewer is only there for convenience, and directly editing the csv files is always a valid fallback.
