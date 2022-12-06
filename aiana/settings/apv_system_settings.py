""" This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>."""


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
                == 'inclined_tables'.
                It is the post distance_y, below the modules within one row
                (including 1x post thickness, as used for array shift).
            'n_apv_system_clones_in_x': number of apv system clones in x-
                direction (for azimuth = 180: cloned towards east). This allows
                to have a larger gap between the modules only every x modules
            'n_apv_system_clones_in_negative_x': as above but to the other side

    other settings are commented inline
    """


class APV_SettingsDefault:
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
                           # this aspect ratio is important to know in which
                           # direction x and y goes for all other quantities
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
            'none'
        ] = 'std'

        self.mountingStructureDict = {
            'material': 'Metal_Aluminum_Anodized',
            'post_thickness_x': 0.2,
            'post_thickness_y': 0.2,
            'n_post_x': 2,
            'module_to_post_distance_x': 0.5,
            'post_distance_x': "auto",
            'inner_table_post_distance_y': 2.6,
            'n_apv_system_clones_in_x': 0,
            'n_apv_system_clones_in_negative_x': 0,
        }
        # not in above dict to allow for Literal definition (other options):
        self.mountingStructureType: Literal[
            'none',
            'framed_single_axes',
            'framed_single_axes_ridgeRoofMods'  # TODO: use mirror instead of
            # rotation so that the copied modules are not facing upwards-down
            'inclined_tables',
            # NOTE the following should only be used in the
            # APV_Syst_InclinedTables_S_Morschenich Child
            'morschenich_fixed'
        ] = 'framed_single_axes'

        self.add_trans_plastic_between_modules: bool = False  # currently only
        # affecting mountingStructureType 'morschenich_fixed'

        # to optionally add a glass plate on the black modules:
        self.glass_modules: bool = False

        self.framed_modules: bool = False

        self.custom_object_rad_txt: str = ''  # to add a custom object, you
        # have to use radiance syntax (https://floyd.lbl.gov/radiance/man_html)

        # ### ground scan area settings
        self.groundScanAreaDict: dict = {
            'start_x': "module_footprint",  # [m]
            'start_y': "module_footprint",  # [m]
            'length_x': "module_footprint",  # [m]
            'length_y': "module_footprint",  # [m]
            'margin_x': 0,  # [m]
            'margin_y': 0,  # [m]
            'shift_x': 0,  # [m] positiv: towards east
            'shift_y': 0,  # [m] positiv: towards north
        }  # NOTE If scan length and start x/y are set to "module_footprint",
        # the gScan area is placed below the foot print of the modules,
        # so that the modules of the main APV_system (not clones) projected
        # to ground (foot print) are just inside of the scan area. To be
        # precise, the scan area starts at the south-west corner of the foot-
        # print and is extended byond the north-east corner to get an integer
        # count of sensor points with respect to the spatial_resolution.
        # You man also enter a float number in [m], whereby start 0,0 is in the
        # center of the apv system only for an uneven row number.

        # shift x/y = 0 means the center of the scan area will be in the center
        # of the apv system, regardless of an even or uneven module count.
        # margins x/y can be added to enlarge (or to reduce by negative
        # values) the scan area symmetrically from both sides.
        # Many geometric quantities, such as e.g. allRows_footprint_x are
        # stored as attributes in the GeometriesHandler(settings) class.

        # ### less important or not in use
        self.module_name = 'SUNFARMING'  # we use only this module type atm

        # for 'framed_single_axes':
        self.enlarge_beams_for_periodic_shadows: bool = False

        # not in use at the moment, as preparation for later, to be used
        # as PVlib input:
        self.moduleSpecs: pd.Series = pd.read_csv(
            Path(__file__).parent.parent.resolve()  # apv package location
            / Path(
                'resources/pv_modules/Sanyo240_moduleSpecs_guestimate.txt'),
            delimiter='\t'
        ).T[0]


class APV_Syst_InclinedTables_S_Morschenich(APV_SettingsDefault):

    def __init__(self):
        super().__init__()
        self.mountingStructureType = 'morschenich_fixed'
        self.add_trans_plastic_between_modules: bool = False
        self.glass_modules: bool = True

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

        self.mountingStructureDict.update({
            'material': 'Metal_Aluminum_Anodized',
            'post_thickness_x': 0.041,
            'post_thickness_y': 0.12,
            'n_post_x': 11,
            'post_distance_x': 4,
            'inner_table_post_distance_y': 2.693,
        })


class APV_ForTesting(APV_SettingsDefault):
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
