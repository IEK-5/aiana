# #
"""struktur notizen:


    gut wäre, wenn man beim brObj instanziieren die Zeit über settings
    definiert und ob stündlich oder kumuliert

    die line_scan_sim ergebnisse dann in
    br_files/results/oct_file_name/hour/scanXY.csv

    merge methode merged dann einfach alles im ordner basierend auf
    oct_file_name und hour

    die merged results dann in Userpaths.results

    """


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
# #
brObj = apv.br_wrapper.BifacialRadianceObj(
    # sim_date_time,
    download_EPW=False
)

brObj.oct_file_name
# #
brObj.view_scene()
# #
brObj.ground_simulation(accuracy='low')
# #
brObj.csv_file_name
# #
fig = apv.utils.plots.plot_heatmap(
    brObj.df_ground_results, 'x', 'y', 'Wm2Ground',
    x_label='x [m]',
    y_label='y [m]',
    z_label='ground insolation [W m$^{-2}$]'
)

apv.utils.files_interface.save_fig(fig, 'apv_ground')
