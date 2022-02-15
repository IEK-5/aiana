# Overview

number of code lines 2.11.2021

648	br_wrapper.py
559	classes/weather_data.py
456	classes/geometries_handler.py
407	classes/APV_evaluation.py
201	utils/plots.py
182	examples/Typical_days_loop.py
181	settings/apv_systems.py
166	utils/files_interface.py
129	examples/debug_geometry.py
106	examples/full_day_morschenich.py
99	classes/sim_datetime.py
79	settings/simulation.py
67	utils/pvlib_wrapper_for_PVGRIP.py
58	utils/time.py
57	examples/checked_board.py
52	utils/evaluation.py
44	examples/dni_dhi_tests.py
43	utils/settings_adjuster.py
40	examples/declined_tables.py
31	apv_main.py
25	examples/declined_tables2.py
19	utils/browse_PVlib_modules.py
15	settings/user_paths.py
10	resources/locations.py
5	utils/init.py
4	classes/init.py
3	settings/init.py
2	utils/pycache/.gitignore
1	resources/init.py

3693 total



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