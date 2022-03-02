# Overview

number of code lines 02.03.2022

   117 classes/br_wrapper.py
   200 classes/evaluator.py
   288 classes/oct_file_creator.py
   170 classes/plotter.py
   120 classes/simulator.py
   565 classes/util_classes/geometries_handler.py
    47 classes/util_classes/settings_grouper.py
    99 classes/util_classes/sim_datetime.py
   514 classes/weather_data.py

    10 resources/locations.py
   366 settings/apv_systems.py
    99 settings/sim_settings.py
    22 settings/user_paths.py

    32 system_studies/apv_main.py
   257 system_studies/Typical_days_loop_S_incl_tables.py

x    52 utils/evaluation.py
   171 utils/files_interface.py
x   308 utils/plotting.py
    90 utils/radiance_utils.py
x    53 utils/settings_adjuster.py
x    58 utils/time.py

    19 utils/not_used_by_code_yet/browse_PVlib_modules.py
    67 utils/not_used_by_code_yet/pvlib_wrapper_for_PVGRIP.py

  3728 total

not part of core code:
   465 classes/APV_Evaluation_mohd_only_reference.py
   205 system_studies/before_restructuring_feb22/Typical_days_loop.py
    51 system_studies/before_restructuring_feb22/checked_board.py
    82 system_studies/before_restructuring_feb22/debug_geometry.py
    40 system_studies/before_restructuring_feb22/declined_tables.py
    25 system_studies/before_restructuring_feb22/declined_tables2.py
   106 system_studies/before_restructuring_feb22/full_day_morschenich.py
    70 system_studies/before_restructuring_feb22/functionality_testing.py

(to get this code lines count:
push to git (no spaces in folder names) and then put following command in bash console:
git ls-files --exclude-standard -- ':!:**/*.[pjs][npv]g' ':!:_tests_and_stuff' ':!:**/*.txt' ':!:**/*.csv' ':!:**/*.pyc' ':!:*__pycache__*' ':!:*__init__*' ':!:*.gitignore*' | xargs wc -l
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