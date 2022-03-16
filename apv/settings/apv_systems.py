
from typing import Literal
from pathlib import Path
import pandas as pd
"""
    all settings can also be overwritten in a working file
    as long as a br_wrapperObj is initializated afterwards.
    See system_studies/apv_main.py for a simple example

    sceneDict [from BR (bifacial_radiance package)]:
        tilt: panel tilt [degree]
        pitch: y-distance between two adjacent module-row-centers [m]
        hub_height: vert. distance: ground to modules center (axis) [m]
        azimuth: panel face direction [degree]
        nMods: modules per row (along x in moduleDict) [-]
        nRows: number of rows [-]

    moduleDict [from BR]:
        x: module width (and array-copy distance for nMods > 1)
        y: module height (commonly y is > x and the module is fixed along x)
        xgap: distance between modules in the row
        ygap: distance between the 2 modules along the collector slope.
        zgap: if there is a torquetube, this is the distance between the
            torquetube and the modules. If there is not a module, zgap
            is the distance between the module and the axis of rotation
            (relevant for tracking systems).
        numpanels: number of panels along y

    cellLevelModuleParams [from BR]:
        = cell parameters within the modules
        numcellsx: number of cells in x [-]
        numcellsy: number of cells in y [-]
        xcellgap: distance between cells in x (along row) [m]
        ycellgap: distance between cells in y (along pitch) [m]
        (cell sizes will be added automatically on init)

    module_form:
        std: standard (one flat solid tile per module) [from BR]
        cell_level: (cells are created as tiles seperated by the gaps)[from BR]
        [new]:
        cell_level_checker_board: cells are left out in a checker board pattern
        EW_fixed: two std modules are facing to east-west in a roof top shape
        cell_level_EW_fixed: combination of cell_level and EW_fixed
        none: no modules (so e.g. only the mounting structure)

    mounting_structure_type [new]:
        none: no structure
        declined_tables: 4 posts per row are near the module row edges
            with different heights to compensate the module tilt
        framed_single_axes: 'n_post_x' posts per row are placed along the tilt
            axis the posts within the rows and between different rows are
            each connected by two horzontal structural beams.

    others are commented inline
    """


class Default:
    """Other presets inheriting from Default"""
    module_name = 'SUNFARMING'

    # bifacial_radiance geometry-inputs

    sceneDict = {'tilt': 20,  # explanations above
                 'pitch': 10,
                 'hub_height': 4.5,
                 'azimuth': 180,
                 'nMods': 10,
                 'nRows': 3,
                 }

    moduleDict = {'x': 0.998,
                  'y': 1.980,
                  'xgap': 0.05,
                  'ygap': 0.05,
                  'zgap': 0,
                  'numpanels': 2
                  }

    moduleSpecs: pd.Series = pd.read_csv(
        Path(__file__).parent.parent.resolve()  # apv package location
        / Path(
            'resources/pv_modules/Sanyo240_moduleSpecs_guestimate.txt'),
        delimiter='\t'
    ).T[0]

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

    mountingStructureDict = {
        'material': 'Metal_Aluminum_Anodized',
        'post_thickness': 0.25,  # mounting structure post thickness [m]
        'n_post_x': 2,  # number of posts along x (along row) [-]
        'module_to_post_distance_x': 0.5,
        'inner_table_post_distance_y': 1.35  # only used by 'declined_tables'
    }
    # not in above dict to allow for literals (other options):
    mounting_structure_type: Literal[
        'none',
        'declined_tables',         # TODO for now this is fixed to Morschenich.
        # Maybe add declined_tables with post count
        # and distance depending on modules again?
        'declined_tables_with_rails',  # see above
        'framed_single_axes'
    ] = 'framed_single_axes'

    # NOTE number of apv system clones in x direction
    # (needed for periodic shadows without border effects, where the sun can
    # shine on the ground from the side in the morning and evening):

    n_apv_system_clones_in_x: int = 0  # for azimuth = 180: cloned towards east
    n_apv_system_clones_in_negative_x: int = 0  # towards west

    # for 'framed_single_axes':
    enlarge_beams_for_periodic_shadows: bool = False

    # to optionally add a glass plate on the black modules:
    glass_modules: bool = False

    # ### ground scan area settings

    # NOTE the scan area is placed below the foot print of the apv system,
    # so that the modules projected to groud (foot print) are just inside of it
    # (all rows, but not the system clones). The visualized object will not
    # influence the simulation results.

    # NOTE one-sided margins [m] can be added to enlarge the field
    # (or to reduce by negative values)
    ground_scan_margin_x: float = 0
    ground_scan_margin_y: float = 0
    # shift scan area [m]
    ground_scan_shift_x: float = 0  # positiv: towards east
    ground_scan_shift_y: float = 0  # positiv: towards north

    # round up to full meters (nice numbers in heatmaps)
    round_up_scan_area_edgeLengths: bool = False


class APV_Syst_InclinedTables_S_Morschenich(Default):

    sceneDict = {'tilt': 20,  # 18.34,
                 'pitch': 7.32,  # 7.46 was a mistake for first 3 sim
                 'hub_height': 3.8,
                 'azimuth': 180,
                 'nMods': 48,  # 24,
                 'nRows': 4,
                 }

    moduleDict = {'x': 0.77,
                  'y': 3.03,  # 0.998,
                  'xgap': 0.11,
                  'ygap': 0,
                  'zgap': 0,  # 0.046,
                  'numpanels': 1
                  }

    mountingStructureDict = {
        'material': 'Metal_Aluminum_Anodized',
        'post_thickness': 0.12,  # mounting structure post thickness [m]
        'n_post_x': 11,  # number of posts along x (along row) [-]
        'module_to_post_distance_x': 0,
        'post_distance_x': 4,
        'inner_table_post_distance_y': 1.35,  # 3 posts, (2.82-0.12)/2 #TODO post thickness?
    }

    mounting_structure_type: Default.mounting_structure_type = \
        'declined_tables_with_rails'


class APV_Morchenich_Checkerboard(Default):
    module_form: Default.module_form = 'cell_level_checker_board'
    # set gap in std module form = 1m
    sceneDict = Default.sceneDict.copy()
    sceneDict['nRows'] = 5

    # 3 clones are needed towards sun for periodic boundary conditions
    # make this depending on sim time to save computation duration
    n_apv_system_clones_in_x: int = 1  # for azimuth = 180: cloned towards east
    n_apv_system_clones_in_negative_x: int = 1  # towards west

    # To reduce sim time and get periodic boundary conditions
    ground_scan_margin_x = 0
    # y reduction (negative margin)
    ground_scan_margin_y = (
        -sceneDict['pitch'] * (sceneDict['nRows']/2-1)-Default.moduleDict['y'])

    # north shift is needed for winter to get
    # periodic boundary conditions in this setup (geometry etc)
    ground_scan_shift_y = sceneDict['pitch']
    enlarge_beams_for_periodic_shadows: bool = True


class APV_Morchenich_EastWest(Default):
    module_form: Default.module_form = 'EW_fixed'

    moduleDict = Default.moduleDict.copy()
    moduleDict['x'] = 55*Default.moduleDict['x']+54*Default.moduleDict['xgap']

    # set gap in std module form = 1m
    sceneDict = {'tilt': 20,
                 'pitch': 10,
                 'hub_height': 4.5,
                 'azimuth': 90,
                 'nMods': 1,  # (10+1)*5,
                 'nRows': 7,
                 }

    mountingStructureDict = Default.mountingStructureDict.copy()
    mountingStructureDict['n_post_x'] = 6
    mountingStructureDict['module_to_post_distance_x'] = 0

    # y reduction (negative margin)
    x_pitch = moduleDict['x']*11/55
    # 11*(Default.moduleDict['x']+Default.moduleDict['xgap'])
    ground_scan_margin_x = -2*x_pitch
    ground_scan_margin_y = (
        -sceneDict['pitch'] * (sceneDict['nRows']/2-1)-Default.moduleDict['y'])
    ground_scan_shift_y = -Default.moduleDict['x']/2 + x_pitch

    enlarge_beams_for_periodic_shadows: bool = True


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

    mountingStructureDict = {
        'material': 'Metal_Aluminum_Anodized',
        'post_thickness': 0.15,  # mounting structure post thickness [m]
        'n_post_x': 3,  # number of posts along x (along row) [-]
        'module_to_post_distance_x': 0
    }

    mounting_structure_type: Default.mounting_structure_type = \
        'declined_tables'
    # add_glass_box = True # for greenhouse, not in use atm
    glass_box_to_APV_distance = 2  # [m]


class SimpleSingleCheckerBoard(Default):
    # as for Perna2019

    module_form: Default.module_form = 'cell_level_checker_board'

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

    mounting_structure_type: Default.mounting_structure_type = 'none'
