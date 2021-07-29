# #
from pathlib import Path
from apv.settings import UserPaths
import importlib as imp

# custom
import apv
imp.reload(apv.settings)
imp.reload(apv.br_wrapper)

simSettings = apv.settings.Simulation()

simSettings.sim_date_time = '06-15_11h'
simSettings.spatial_resolution = 0.1
simSettings.sky_gen_mode = 'gendaylit'
#simSettings.sim_mode = 'cell_level_checker_board'
simSettings.sim_name = simSettings.sim_mode

weather_file = UserPaths.bifacial_radiance_files_folder / \
    Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

brObj = apv.br_wrapper.BifacialRadianceObj(
    simSettings=simSettings,
    weather_file=weather_file  # without this, download happens automatically
)

brObj.view_scene(
    # view_name='module_zoom'
)

# #
brObj.ground_simulation()

# #
brObj.plot_ground_insolation()
