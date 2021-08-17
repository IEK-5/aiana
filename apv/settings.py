'''Classes are used here only to group the static parameters'''

from pathlib import Path
from apv import resources as res
import datetime as dt
from typing import Literal


class Simulation:
    sim_name = 'APV_Floating'  # also used as first part of the .oct file name

    # speed up options

    # Spatial resolution between sensors
    spatial_resolution = 5  # 0.15  # [m]
    # ray tracing accuracy used in br.analysisObj.analysis()
    ray_tracing_accuracy = 'low'  # 'high' does not improve accuracy much but
    # sim time is increased by x3-x4
    use_multi_processing = True
    only_ground_scan = True  # if False the backscan will be implemented too
    add_mountring_structure = True

    # sky generation type:'gendaylit' or 'gencumsky'
    sky_gen_mode: Literal['gendaylit', 'gencumsky'] = 'gendaylit'

    # time settings
    sim_date_time = '06-15_11h'  # used as second part of the .oct file name

    if sky_gen_mode == 'gencumsky':
        # Insert start date of the year as [month,day,hour]
        startdt = [1, 1, 12]
        # Insert end date of year as [month,day,hour]
        enddt = [3, 31, 23]

    # hour_of_year = 4020
    # start_time = ''
    # end_time = ''
    # time_step = '1h'

    # location
    apv_location = res.locations.APV_Morschenich

    # ground
    ground_albedo = 0.25  # grass

    module_name = 'SUNFARMING'

    # bifacial_radiance geometry-inputs

    """ sceneDict:
    tilt: panel tilt [degree]
    pitch: distance between two adjacent rows [m]
    hub_height: vert. distance: ground to modules [m]
    azimuth: panel face direction [degree]
    nMods: modules per row (along x in moduleDict) [-]
    nRows: number of rows [-] """
    sceneDict = {
        'tilt': 20,
        'pitch': 10,
        'hub_height': 4.5,
        'azimuth': 180,
        'nMods': 10,
        'nRows': 3,
    }

    """ moduleDict:
    x: module width (and array-copy distance for nMods > 1)
    y: module height (commonly y is > x and the module is fixed along x)
    xgap: Distance between modules in the row
    ygap: Distance between the 2 modules along the collector slope.
    zgap: If there is a torquetube, this is the distance between the
        torquetube and the modules. If there is not a module, zgap
        is the distance between the module and the axis of rotation
        (relevant for tracking systems).
    numpanels: number of panels along y """
    moduleDict = {
        'x': 0.998,
        'y': 1.980,
        'xgap': 0.002,
        'ygap': 0.05,
        'zgap': 0,
        'numpanels': 2
    }

    module_form: Literal[
        'std',
        'cell_level',
        'cell_level_checker_board',
        'EW_fixed',  # at the moment second modul of roof is created in the
        # text input for br.radObj.make_module(),
        # and the tilt is happening later in br.radObj.make_scene()
        # the second module is facing upwards-down, might be a problem later
        'cell_level_EW_fixed'
    ] = 'std'

    cellLevelModuleParams = {
        'numcellsx': 6,  # has to be an even number at the moment
        'numcellsy': 12,  # has to be an even number at the moment
        'xcellgap': 0.02,
        'ycellgap': 0.02
    }

    scene_camera_dicts: dict = {
        'total': {
            'cam_pos_x': -14,   # depth
            'cam_pos_y': -1.6,   # left / right
            'cam_pos_z': 8,     # height
            'view_direction_x': 1.581,
            'view_direction_y': 0,
            'view_direction_z': -0.519234,
            'horizontal_view_angle': 120,  # [degree]
            'vertical_view_angle': 90  # [degree]
        },
        'module_zoom': {
            'cam_pos_x': -5,   # depth
            'cam_pos_y': -1.1,   # left / right
            'cam_pos_z': 6.5,     # height
            'view_direction_x': 1.581,
            'view_direction_y': 0,
            'view_direction_z': -1.919234,
            'horizontal_view_angle': 120,  # [degree]
            'vertical_view_angle': 90  # [degree]
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

# #
