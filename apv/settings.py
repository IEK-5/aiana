'''Classes are used here only to group the static parameters'''

from pathlib import Path
from apv import resources as res


class Simulation:
    name = 'APV_Floating'  # also used as first part of the .oct file name

    # Spatial resolution between sensors
    spatial_resolution = 10  # 0.5  # [m]
    # ray tracing accuracy used in br.analysisObj.analysis()
    ray_tracing_accuracy = 'high'  # 'low' or 'high'
    # sky generation type
    sky_gen_type = 'gendaylit'  # 'gendaylit' or (later) 'gencumsky'

    # time settings
    sim_date_time = '06-15_11h'  # used as second part of the .oct file name

    # hour_of_year = 4020
    # start_time = ''
    # end_time = ''
    # time_step = '1h'

    # location
    apv_location = res.locations.APV_Morschenich

    # ground
    ground_albedo = 0.25  # grass

    module_type = 'SUNFARMING'

    # bifacial_radiance geometry-inputs

    """

    ### moduleDict:
    x: module width
    y: module height (commonly y is > x and the module is fixed along x)
    xgap: Distance between modules in the row
    ygap: Distance between the 2 modules along the collector slope.
    zgap: If there is a torquetube, this is the distance between the
        torquetube and the modules. If there is not a module, zgap
        is the distance between the module and the axis of rotation
        (relevant for tracking systems).
    numpanels: number of panels along y

    ### sceneDict:
    tilt: panel tilt [degree]
    pitch: distance between two adjacent rows [m]
    hub_height: vert. distance: ground to modules [m]
    azimuth: panel face direction [degree]
    nMods: modules per row (along x in moduleDict) [-]
    nRows: number of rows [-]

    """
    moduleDict = {
        'x': 0.998,
        'y': 1.980,
        'xgap': 0.002,
        'ygap': 0.05,
        'zgap': 0,
        'numpanels': 2
    }

    sceneDict = {
        'tilt': 20,
        'pitch': 10,
        'hub_height': 4.5,
        'azimuth': 180,
        'nMods': 10,
        'nRows': 3
    }

    scene_camera_dicts: dict = {
        'total': {
            'cam_pos_x': -15,   # depth
            'cam_pos_y': -1.6,   # left / right
            'cam_pos_z': 6,     # height
            'view_direction_x': 1.581,
            'view_direction_y': 0,
            'view_direction_z': -0.519234,
            'horizontal_view_angle': 110,  # [degree]
            'vertical_view_angle': 45  # [degree]
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
