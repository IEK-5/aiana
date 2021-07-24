# #
"""struktur notizen:

    die line_scan_sim ergebnisse dann in
    br_files/results/oct_file_name/hour/scanXY.csv

    merge methode merged dann einfach alles im ordner basierend auf
    oct_file_name und hour

    die merged results dann in Userpaths.results

    """


import seaborn as sns
import pandas as pd
from pathlib import Path
from apv.utils import time
from apv.utils import files_interface as fi
from apv.settings import UserPaths
from apv.settings import Simulation as s
import subprocess
import importlib as imp
import os
import bifacial_radiance as br

# custom
import apv
imp.reload(apv.settings)
imp.reload(apv.br_wrapper)

simSettings = apv.settings.Simulation()

simSettings.sim_date_time = '06-15_11h'
simSettings.checker_board = False
# simSettings.sky_gen_type = 'gencumsky'

weather_file = UserPaths.bifacial_radiance_files_folder / \
    Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

brObj = apv.br_wrapper.BifacialRadianceObj(
    simSettings=simSettings,
    weather_file=weather_file  # without this, download happens automatically
)

brObj.view_scene(
    view_name='module_zoom'
)
# #
df = brObj.ground_simulation()
# #
data = df.pivot('y', 'x', 'Wm2Ground')
print(data)
# #
sns.heatmap(
    data,
    annot=False,
    linewidths=0,
    # only relevant for later if there are more than one ax
    square=True,
    xticklabels=2,  # skip every second tick label

)
# #
imp.reload(apv.utils.plots)
fig = apv.utils.plots.plot_heatmap(
    df, 'y', 'x', 'Wm2Ground',
    x_label='x [m]', y_label='y [m]',
    z_label='ground insolation [W m$^{-2}$]'
)

apv.utils.files_interface.save_fig(fig, brObj.oct_file_name)

# #
# loop through hours:

simSettings = apv.settings.Simulation()
simSettings.spatial_resolution = 0.5

for hour in range(12, 20, 2):
    simSettings.sim_date_time = '06-15_'+str(hour)+'h'
    brObj = apv.br_wrapper.BifacialRadianceObj(
        simSettings=simSettings,
        download_EPW=False
    )
    brObj.ground_simulation()

    fig = apv.utils.plots.plot_heatmap(
        brObj.df_ground_results, 'y', 'x', 'Wm2Ground',
        x_label='x [m]', y_label='y [m]',
        z_label='ground insolation [W m$^{-2}$]',
        plot_title=simSettings.sim_date_time.replace('_', ' ')
    )

    apv.utils.files_interface.save_fig(fig, brObj.oct_file_name)

# #