# Intro
apv = agri(photo)voltaic

# Installation

Bifacial-radiance
Installation guide: https://www.youtube.com/watch?v=4A9GocfHKyM
Nach der Radiance Installation in Windows 10 nach „Systemumgebungsvariablen bearbeiten“ suchen und prüfen ob der Radiance-Pfad „…/Radiance/bin“ wirklich in der Umgebungsvariable „Pfad“ drin ist (war bei mir erst nicht). Dann gegebenenfalls manuell eintragen.


Software training: https://www.youtube.com/watch?v=1X9L-R-RVGA
PHD defense of Ms. Pelaez: https://www.youtube.com/watch?v=11Jp7GqzLPQ

radiance user manual: https://floyd.lbl.gov/radiance/refer/usman2.pdf

# toml dependencies leads to apv installation error??
# Overview

number of code lines 02.03.2022

    47 classes/br_wrapper.py
   188 classes/evaluator.py
   290 classes/oct_file_creator.py
   170 classes/plotter.py
   117 classes/simulator.py
   601 classes/util_classes/geometries_handler.py
    47 classes/util_classes/settings_grouper.py
    67 classes/util_classes/sim_datetime.py
   479 classes/weather_data.py

    10 resources/locations.py
   362 settings/apv_systems.py
    94 settings/sim_settings.py
    22 settings/user_paths.py

   257 system_studies/Typical_days_loop_S_incl_tables.py
    33 system_studies/apv_main.py

    51 utils/RMSE_MBE.py
   172 utils/files_interface.py
    19 utils/not_used_by_code_yet/browse_PVlib_modules.py
    67 utils/not_used_by_code_yet/pvlib_wrapper_for_PVGRIP.py
    35 utils/not_used_by_code_yet/time.py
   308 utils/plotting.py
    90 utils/radiance_utils.py

  3530 total



14.06.2022

    85 classes/br_wrapper.py
   178 classes/evaluator.py
   440 classes/oct_file_handler.py
   240 classes/plotter.py
   262 classes/simulator.py
   727 classes/util_classes/geometries_handler.py
    10 classes/util_classes/print_hider.py
    55 classes/util_classes/settings_grouper.py
    59 classes/util_classes/sim_datetime.py
   494 classes/weather_data.py

   167 imports.txt
   115 requirements.txt
    10 resources/locations.py

   324 settings/apv_systems.py
   138 settings/sim_settings.py
    22 settings/user_paths.py
    62 settings/view_settings.py

   290 system_studies/Typical_days_loop_S_incl_tables.py
   162 system_studies/anti_bug_settings_testing.py
   124 system_studies/comparing_plots/epw_vs_ads.py
   119 system_studies/comparing_plots/subsets_boxplot.py
   155 system_studies/comparing_plots/subsets_heatmaps_subplots.py
    92 system_studies/comparing_plots/with_vs_without_extraglass.py
    16 system_studies/minimal_example.py
   215 system_studies/study_subset_variation.py

    51 utils/RMSE_MBE.py
   179 utils/files_interface.py
    19 utils/not_used_by_code_yet/browse_PVlib_modules.py
    67 utils/not_used_by_code_yet/pvlib_wrapper_for_PVGRIP.py
    35 utils/not_used_by_code_yet/time.py
   351 utils/plotting_utils.py
    95 utils/radiance_utils.py
   175 utils/study_utils.py
  5537 total


(to get this code lines count:
push to git (no spaces in folder names) and then put following command in bash console within apv subdirectory as working path:

git ls-files --exclude-standard -- ':!:**/*.[pjs][npv]g' ':!:_tests_and_stuff' ':!:system_studies/before_restructuring_feb22' ':!:*/*only_reference*' ':!:**/*.txt' ':!:**/*.csv' ':!:**/*.pyc' ':!:*__pycache__*' ':!:*__init__*' ':!:*.gitignore*' | xargs wc -l

)

# HOW TO install the apv package in vscode

- make sure that the file path in the terminal ist the one of the
package folder (agri-pv), in which "setup.py" is localized. If you have several folders in your workspace right click agri-pv and choose "Open in Integrated Terminal"

- run command:

      pip install -e .

- restart vscode

- if this did not help, try
    pip uninstall apv
    restart
    pip install -e .
