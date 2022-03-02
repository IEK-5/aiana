# Intro
apv = agri(photo)voltaic

# Overview

number of code lines 02.03.2022

   117 classes/br_wrapper.py
   200 classes/evaluator.py
   288 classes/oct_file_creator.py
   170 classes/plotter.py
   120 classes/simulator.py
   601 classes/util_classes/geometries_handler.py
    47 classes/util_classes/settings_grouper.py
    67 classes/util_classes/sim_datetime.py
   514 classes/weather_data.py

    10 resources/locations.py
   366 settings/apv_systems.py
    99 settings/sim_settings.py
    22 settings/user_paths.py

   257 system_studies/Typical_days_loop_S_incl_tables.py
    32 system_studies/apv_main.py

    51 utils/RMSE_MBE.py
   172 utils/files_interface.py
    19 utils/not_used_by_code_yet/browse_PVlib_modules.py
    67 utils/not_used_by_code_yet/pvlib_wrapper_for_PVGRIP.py
    35 utils/not_used_by_code_yet/time.py
   308 utils/plotting.py
    90 utils/radiance_utils.py
  3656 total

(to get this code lines count:
push to git (no spaces in folder names) and then put following command in bash console:
git ls-files --exclude-standard -- ':!:**/*.[pjs][npv]g' ':!:_tests_and_stuff' ':!:system_studies/before_restructuring_feb22' ':!:*/*only_reference*' ':!:**/*.txt' ':!:**/*.csv' ':!:**/*.pyc' ':!:*__pycache__*' ':!:*__init__*' ':!:*.gitignore*' | xargs wc -l
)

# HOW TO install the package in vscode

- make sure that the file path in the terminal ist the one of the
package folder (agri-pv), in which "setup.py" is localized. If you have several folders in your workspace right click agri-pv and choose "Open in Integrated Terminal"

- run command:

      pip install -e .

- restart vscode

- if this did not help, try
    pip uninstall apv
    restart
    pip install -e .




and replace
    cmd = "rtrace -i -ab 2 -aa .1 -ar 256 -ad 2048 -as 256 -h -oovs " + octfile
with
    cmd = "rtrace -i -ab 2 -aa .1 -ar 256 -ad 1024 -as 256 -h -oovs " + octfile

in main.py (also in BR)
(due to http://designbuilder.co.uk/helpv3.0/Content/Daylighting%20Calculation%20Options.htm#Ambient4)