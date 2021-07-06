'''Classes are used here only to group the static parameters'''

from pathlib import Path
from apv import resources as res


class Simulation:
    name = 'APV_Floating'  # also used as first part of the .oct file name

    # Spatial resolution between sensors
    spatial_resolution = 4  # [m]
    # ray tracing accuracy used in br.analysisObj.analysis()
    ray_tracing_accuracy = 'low'  # 'low' or 'high'

    # time settings
    sim_date_time = '06-15_10h'  # used as second part of the .oct file name

    # hour_of_year = 4020
    # start_time = ''
    # end_time = ''
    # time_step = '1h'

    # PVlib location object
    apv_location = res.locations.APV_Morschenich

    # object containing dictionaries for bifacial_radiance geometry-inputs
    module_type = 'SUNFARMING'
    geometries = res.geometry_presets.APV_Morschenich

    # ground
    ground_albedo = 0.25  # grass

    scene_camera_dicts: dict[dict[str, float]] = {
        'total': {
            'cam_pos_x': -15,   # depth
            'cam_pos_y': -1.6,   # left / right
            'cam_pos_z': 6,     # height
            'view_direction_x': 1.581,
            'view_direction_y': 0,
            'view_direction_z': -0.519234,
            'horizontal_view_angle': 110,
            'vertical_view_angle': 45
        }
    }


class UserPaths:
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
