
from typing import Literal
from pathlib import Path
import pandas as pd
"""
    all settings can also be oself.verwritten in a working file
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
        cell_gaps: (cells are created as tiles seperated by the gaps)[from BR]
        [new]:
        checker_board: cells are left out in a checker board pattern
        roof_for_EW: two std modules are facing to east-west in a roof top shape
        cell_gaps_roof_for_EW: combination of cell_gaps and roof_for_EW
        none: no modules (so e.g. only the mounting structure)

    mountingStructureType [new]:
        none: no structure
        inclined_tables: 'n_post_x' posts per row are near the module row edges
            with different heights to compensate the module tilt
        framed_single_axes: 'n_post_x' posts per row are placed along the tilt
            axis the posts within the rows and between different rows are
            each connected by two horzontal structural beams.

    mountingStructureDict [new]:
            'material': 'Metal_Aluminum_Anodized',
                or other rad material, e.g.'black'
            'post_thickness_x': mounting structure post thickness in x [m]
            'post_thickness_y': mounting structure post thickness in y [m]
            'n_post_x': 2,  # number of posts along x (along row) [-]
            'module_to_post_distance_x': in top down view, distance from
                the module edge to post edge (only at one side, or symmetrical,
                if 'post_distance_x' is set to "auto")
            'post_distance_x': float, or "auto" for symmetric adaption
            'inner_table_post_distance_y': only used, if mountingStructureType
                == 'inclined_tables'
            'n_apv_system_clones_in_x': number of apv system clones in x-
                direction (for azimuth = 180: cloned towards east). This allows
                to have a larger gap between the modules only every x modules
            'n_apv_system_clones_in_negative_x': as above but to the other side

    other settings are commented inline
    """


class Default:
    """Other presets inherit from this Default"""

    def __init__(self):
        # ### bifacial_radiance geometry-inputs
        self.sceneDict = {'tilt': 20,  # explanations above
                          'pitch': 10,
                          'hub_height': 4.5,
                          'azimuth': 180,
                          'nMods': 10,
                          'nRows': 3,
                          }

        self.moduleDict = {'x': 0.998,
                           'y': 1.980,
                           'xgap': 0.05,
                           'ygap': 0.05,
                           'zgap': 0,  # no effect, not yet implemented
                           'numpanels': 2
                           }

        self.cellLevelModuleParams = {
            'numcellsx': 6,  # has to be an even number at the moment
            'numcellsy': 12,  # has to be an even number at the moment
            'xcellgap': 0.02,
            'ycellgap': 0.02
        }

        # ### new input
        self.module_form: Literal[  # Literal for auto-completition in vs-code
            'std',
            'cell_gaps',
            'checker_board',
            'roof_for_EW',  # TODO glass part will not result in
            # roof shape at the moment, since br.radObj.make_module() is used
            # resulting in standard shape (straight)

            # and the tilt is happening later in br.radObj.make_scene()
            # so the second module is facing upwards-down, might be a problem
            # later

            # # 'cell_gaps_roof_for_EW',  # not implemented atm
            'none'
        ] = 'std'

        self.mountingStructureDict = {
            'material': 'Metal_Aluminum_Anodized',
            'post_thickness_x': 0.2,
            'post_thickness_y': 0.2,
            'n_post_x': 2,
            'module_to_post_distance_x': 0.5,
            'post_distance_x': "auto",
            'inner_table_post_distance_y': 1.35,
            'n_apv_system_clones_in_x': 0,
            'n_apv_system_clones_in_negative_x': 0,
        }
        # not in above dict to allow for Literal definition (other options):
        self.mountingStructureType: Literal[
            'none',
            'framed_single_axes',
            'framed_single_axes_ridgeRoofMods'
            'inclined_tables',
            'morschenich_fixed',  # NOTE this one should only be used in the
            # APV_Syst_InclinedTables_S_Morschenich Child
        ] = 'framed_single_axes'

        # ### ground scan area settings
        self.gScanAreaDict: dict = {
            'ground_scan_margin_x': 0,  # [m]
            'ground_scan_margin_y': 0,  # [m]
            'ground_scan_shift_x': 0,  # [m] positiv: towards east
            'ground_scan_shift_y': 0,  # [m] positiv: towards north
            'round_up_scan_edgeLengths': False  # round up to full meters
        }  # NOTE the gScan area is placed below the foot print of the modules,
        # so that the modules projected to groud (foot print) are just inside
        # of it (all rows, but not the system clones). The visualized object
        # will not be included in the ray tracing simulation and thus not
        # influence the results.
        # One-sided margins [m] can be added to enlarge the field
        # (or to reduce by negative values).

        # ### less important or not in use
        self.module_name = 'SUNFARMING'  # we use only this module type atm

        # for 'framed_single_axes':
        self.enlarge_beams_for_periodic_shadows: bool = False

        # to optionally add a glass plate on the black modules:
        self.glass_modules: bool = False
        self.framed_modules: bool = False
        # NOTE Adding glass and frames creates it as in BR
        # for module_form = 'std', which is nice for cell level
        # and for checker board but not suitable for roof yet.
        # TODO make roof out of BR module with nPanels = 1?

        self.moduleSpecs: pd.Series = pd.read_csv(
            Path(__file__).parent.parent.resolve()  # apv package location
            / Path(
                'resources/pv_modules/Sanyo240_moduleSpecs_guestimate.txt'),
            delimiter='\t'
        ).T[0]


class APV_Syst_InclinedTables_S_Morschenich(Default):

    def __init__(self):
        super().__init__()

        self.sceneDict = {'tilt': 20,  # 18.34,
                          'pitch': 7.32,  # 7.46 was a mistake for first 3 sim
                          'hub_height': 3.8,
                          'azimuth': 180,
                          'nMods': 48,  # 24,
                          'nRows': 4,
                          }

        self.moduleDict = {'x': 0.83,
                           'y': 3.03,  # 0.998,
                           'xgap': 0.05,
                           'ygap': 0,
                           'zgap': 0,  # 0.046,
                           'numpanels': 1
                           }

        self.mountingStructureType = 'morschenich_fixed'

        self.mountingStructureDict.update({
            'material': 'Metal_Aluminum_Anodized',
            'post_thickness_x': 0.041,
            'post_thickness_y': 0.12,
            'n_post_x': 11,
            'post_distance_x': 4,
            'inner_table_post_distance_y': 1.35,
            # at outer frame for 3 posts: (2.82-0.12)/2 = 1.35
        })


class APV_ForTesting(Default):
    def __init__(self):
        super().__init__()

        self.sceneDict = {'tilt': 30,
                          'pitch': 10,  # "row width"
                          'hub_height': 5,
                          'azimuth': 180,
                          'nMods': 4,
                          'nRows': 2}

        self.mountingStructureType = 'framed_single_axes'
        self.mountingStructureDict['module_to_post_distance_x'] = 0.5
        self.mountingStructureDict['n_apv_system_clones_in_x'] = 1