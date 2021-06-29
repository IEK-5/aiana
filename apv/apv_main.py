# #
import importlib as imp
import os
import bifacial_radiance as br

# custom
import apv
from apv.settings import Simulation as s
from apv.settings import UserPaths
from apv.utils import files_interface as fi
from apv.utils import time
# #
imp.reload(apv.br_wrapper)

# if __name__ == "__main__":

radObj, scene, oct_file_name, met_data = apv.br_wrapper.setup_br()


# #
# kann man noch in den wrapper packen mit std view settings aus settings

view_fp = UserPaths.bifacial_radiance_files_folder / 'views/overall.vp'
with open(view_fp, 'w') as f:
    f.write('rvu -vtv -vp '              # vp = view port
            + '-15 '                     # X (depth)
            + '-1.8 '                    # Y (left / right)
            + '6 '                       # Z (height)
            + '-vd 1.581 0 -0.519234 '   # vd = view direction
            + '-vu 0 0 1 '               # vu = view "Up" ???
            + '-vh 110 -vv 45 '          # vh/vv = horizonor
            + '-vs 0 -vl 0')             # vs/vl:
apv.br_wrapper.view_oct_file_with_rvu(
    view_fp=view_fp, oct_file_name=oct_file_name)

# #
apv.br_wrapper.ground_simulation(radObj, scene, oct_file_name, 'low')

# #
timeindex = 4020  # muss noch automatisiert werden
ygrid = apv.br_wrapper.get_ygrid()
final_ground = apv.br_wrapper.merge_linescans(timeindex, ygrid, radObj)
final_ground

# #
# final_ground = apv.utils.files_interface.df_from_file(
#    apv.settings.UserPaths.results_folder / 'ground_merged.csv')

fig = apv.utils.plots.plot_heatmap(
    final_ground, 'x', 'y', 'Wm2Ground',
    x_label='x [m]',
    y_label='y [m]',
    z_label='ground insolation [W m$^{-2}$]'
)

apv.utils.files_interface.save_fig(fig, 'apv_ground')
