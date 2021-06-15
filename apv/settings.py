'''Classes are used here only to group the static parameters'''

from pathlib import Path

from apv import resources as res


class UserPaths():
    root_folder = Path().home().resolve() / 'Documents' / 'agri-PV'

    # bifacial_radiance
    # settings.UserPaths.br_folder
    radiance_files_folder = root_folder / 'radiance_files'

    # for plots and tables
    results_folder = root_folder / 'results'
    # for weather data
    data_download_folder = root_folder / 'data_downloads'


class Simulation():
    name = 'APV_Floating'  # will be used as .oct file name

    # time settings
    hour_of_year = 4020
    start_time = ''
    end_time = ''
    time_step = '1h'

    # PVlib location object
    apv_location = res.locations.APV_Morschenich

    # object containing dictionaries for bifacial_radiance geometry-inputs
    moduletype = 'SUNFARMING'
    geometries = res.geometry_presets.APV_Morschenich

    # ground
    ground_albedo = 0.25  # grass
