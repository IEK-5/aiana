# #
from pathlib import Path
from apv.settings import UserPaths
import importlib as imp
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
    # weather_file=weather_file  # without this, download happens automatically
)
# #
brObj.view_scene(
    view_name='module_zoom'
)
# #
# can take hours depending on the settings
brObj.ground_simulation()

# #
brObj.plot_ground_insolation()

# #
