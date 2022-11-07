# #

from pathlib import Path
from aiana.settings import UserPaths
import importlib as imp

# custom
import aiana
imp.reload(aiana.settings)
imp.reload(aiana.classes.br_wrapper)

simSettings = aiana.settings.sim_settings.Simulation()
simSettings.spatial_resolution = 0.5

weather_file = UserPaths.radiance_input_files_folder / \
    Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

for hour in range(12, 20, 2):
    simSettings.sim_date_time = '06-15_'+str(hour)+'h'
    aiana = aiana.classes.br_wrapper.BR_Wrapper(
        SimSettings=simSettings,
        download_EPW=False
    )
    aiana.run_raytracing_simulation()

    aiana.plot_ground_insolation()


# #
