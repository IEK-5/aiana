# #

from pathlib import Path
from apv.settings import UserPaths
import importlib as imp

# custom
import apv
imp.reload(apv.settings)
imp.reload(apv.br_wrapper)

simSettings = apv.settings.Simulation()
simSettings.spatial_resolution = 0.5

weather_file = UserPaths.bifacial_radiance_files_folder / \
    Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

for hour in range(12, 20, 2):
    simSettings.sim_date_time = '06-15_'+str(hour)+'h'
    brObj = apv.br_wrapper.BifacialRadianceObj(
        simSettings=simSettings,
        download_EPW=False
    )
    brObj.ground_simulation()

    brObj.plot_ground_insolation()


# #
