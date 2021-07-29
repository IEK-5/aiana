"""low res for fast results"""

# #
from pathlib import Path
from apv.settings import UserPaths
import importlib as imp

# custom
import apv
imp.reload(apv.settings)
imp.reload(apv.br_wrapper)

simSettings = apv.settings.Simulation()


simSettings.use_multi_processing = False

simSettings.sim_date_time = '06-15_11h'
simSettings.checker_board = False
simSettings.spatial_resolution = 10
simSettings.sky_gen_mode = 'gendaylit'
simSettings.sim_name = 'debug'

weather_file = UserPaths.bifacial_radiance_files_folder / \
    Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

brObj = apv.br_wrapper.BifacialRadianceObj(
    simSettings=simSettings,
    weather_file=weather_file  # without this, download happens automatically
)
# #
# brObj.view_scene(
# view_name='module_zoom'
# )


# #

brObj.ground_simulation()

# #
brObj.plot_ground_insolation()


# #
