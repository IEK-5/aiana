'''Classes are used here only to group the static parameters'''

from pathlib import Path

from apv import resources as res


class UserPaths():
    """Paths for working folder, radiance folder
    """
    root: Path = Path().home().resolve() / 'Documents/agri-PV'

    # bifacial_radiance
    # settings.UserPaths.br_folder
    bifacial_radiance_files_folder: Path = root / 'bifacial_radiance_files'

    # for plots and tables
    results_folder: Path = root / 'results'
    # for weather data
    data_download_folder: Path = root / 'data_downloads'


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
    module_type = 'SUNFARMING'
    geometries = res.geometry_presets.APV_Morschenich

    # ground
    ground_albedo = 0.25  # grass

    # Spatial resolution between sensors in [m]
    spatial_resolution = 1
