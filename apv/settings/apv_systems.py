
from typing import Literal
"""
    sceApneDict:
    tilt: panel tilt [degree]
    pitch: distance between two adjacent module-rows [m]
    hub_height: vert. distance: ground to modules [m]
    azimuth: panel face direction [degree]
    nMods: modules per row (along x in moduleDict) [-]
    nRows: number of rows [-]

    moduleDict:
    x: module width (and array-copy distance for nMods > 1)
    y: module height (commonly y is > x and the module is fixed along x)
    xgap: Distance between modules in the row
    ygap: Distance between the 2 modules along the collector slope.
    zgap: If there is a torquetube, this is the distance between the
        torquetube and the modules. If there is not a module, zgap
        is the distance between the module and the axis of rotation
        (relevant for tracking systems).
    numpanels: number of panels along y """


class Default:
    """APV_Syst_Morschenich"""
    module_name = 'SUNFARMING'

    # bifacial_radiance geometry-inputs

    sceneDict = {'tilt': 20,
                 'pitch': 10,
                 'hub_height': 4.5,
                 'azimuth': 180,
                 'nMods': 10,
                 'nRows': 3,
                 }

    moduleDict = {'x': 0.998,
                  'y': 1.980,
                  'xgap': 0.005,
                  'ygap': 0.05,
                  'zgap': 0,
                  'numpanels': 2
                  }

    cellLevelModuleParams = {
        'numcellsx': 6,  # has to be an even number at the moment
        'numcellsy': 12,  # has to be an even number at the moment
        'xcellgap': 0.02,
        'ycellgap': 0.02
    }

    module_form: Literal[
        'std',
        'cell_level',
        'cell_level_checker_board',
        'EW_fixed',  # at the moment second modul of roof is created in the
        # text input for br.radObj.make_module(),
        # and the tilt is happening later in br.radObj.make_scene()
        # the second module is facing upwards-down, might be a problem later
        'cell_level_EW_fixed',
        'none'
    ] = 'std'

    mounting_structure_type: Literal[
        'none', 'declined_tables', 'framed_single_axes'] = 'framed_single_axes'

    scene_camera_dicts: dict = {
        'total': {'cam_pos_x': -20,   # depth
                  'cam_pos_y': 0,   # left / right
                  'cam_pos_z': 16,     # height
                  'view_direction_x': 0,
                  'view_direction_y': 1,
                  'view_direction_z': -1,
                  'horizontal_view_angle': 120,  # [degree]
                  'vertical_view_angle': 90  # [degree]
                  },
        'module_zoom': {'cam_pos_x': -5,   # depth
                        'cam_pos_y': -1.1,   # left / right
                        'cam_pos_z': 6.5,     # height
                        'view_direction_x': 1.581,
                        'view_direction_y': 0,
                        'view_direction_z': -2,
                        'horizontal_view_angle': 120,  # [degree]
                        'vertical_view_angle': 90  # [degree]
                        },
        'top_down': {'cam_pos_x': 0,   # depth
                     'cam_pos_y': 0,   # left / right
                     'cam_pos_z': 10,     # height
                     'view_direction_x': 0,
                     'view_direction_y': 0.001,
                     'view_direction_z': -1,
                     'horizontal_view_angle': 40,  # [degree]
                     'vertical_view_angle': 30  # [degree]
                     },
    }
    glass_modules: bool = False
    # one-sided margins [m]
    ground_scan_margin_x: float = 8
    ground_scan_margin_y: float = 4
    # shift scan area [m]
    ground_scan_shift_x: float = -1  # positiv: towards east
    ground_scan_shift_y: float = 1  # positiv: towards north

    round_up_field_dimensions: bool = True

    extra_customObject_rad_text: str = None


class APV_Syst_InclinedTables_Juelich(Default):

    sceneDict = {'tilt': 15,
                 'pitch': 10,
                 'hub_height': 2.25,
                 'azimuth': 225,
                 'nMods': 10,
                 'nRows': 2,
                 }

    moduleDict = {'x': 1.980,
                  'y': 0.998,
                  'xgap': 0.1,
                  'ygap': 0.1,
                  'zgap': 0,
                  'numpanels': 5
                  }

    mounting_structure_type: Default.mounting_structure_type = \
        'declined_tables'
    add_glass_box = True
    glass_box_to_APV_distance = 2  # [m]
    scene_camera_dicts = Default.scene_camera_dicts
    scene_camera_dicts['total'] = {'cam_pos_x': -21.5,   # depth
                                   'cam_pos_y': 6.9,   # left / right
                                   'cam_pos_z': 1,     # height
                                   'view_direction_x': 0.9863,
                                   'view_direction_y': -0.1567,
                                   'view_direction_z': -0.0509,
                                   'horizontal_view_angle': 60,  # [degree]
                                   'vertical_view_angle': 40  # [degree]
                                   }


class SimpleForCheckerBoard(Default):
    # as for Perna2019

    sceneDict = {'tilt': 36.6,
                 'pitch': 7.0,  # "row width"
                 'hub_height': 5,
                 'azimuth': 180,
                 'nMods': 1,
                 'nRows': 1,
                 }

    moduleDict = {'x': 6.0,
                  'y': 3.0,
                  'xgap': 0.001,
                  'ygap': 0.001,
                  'zgap': 0,
                  'numpanels': 1
                  }

    module_form: Default.module_form = 'cell_level_checker_board'
    mounting_structure_type: Default.mounting_structure_type = 'none'
