"""documentation links

    GENBOX (create a box with a certain size)
    https://floyd.lbl.gov/radiance/man_html/genbox.1.html

    GENREV (to create tubes, rings, donats, etc.)
    https://floyd.lbl.gov/radiance/man_html/genrev.1.html

    XFORM (translate, rotate, make arrays):
    https://floyd.lbl.gov/radiance/man_html/xform.1.html

    """

import numpy as np
from typing import Literal
import inspect
import apv
from apv.settings.apv_systems import Default as APV_SystSettings

import apv.settings.user_pathes as user_pathes
from pathlib import Path


class GeometriesHandler:
    """
    x_field (int): lengths of the groundscan area in x direction
    according to scene
    y_field (int): lengths of the groundscan area in y direction

    """  # TODO shift explanation in line comments to docstring

    def __init__(
            self,
            SimSettings: apv.settings.simulation.Simulation,
            APV_SystSettings: apv.settings.apv_systems.Default,
            debug_mode=False
    ):
        self.SimSettings: apv.settings.simulation.Simulation = SimSettings
        self.APV_SystSettings: apv.settings.apv_systems.Default = \
            APV_SystSettings
        self.debug_mode = debug_mode

        self.APV_SystSettings = APV_SystSettings
        self.mod = self.APV_SystSettings.moduleDict
        self.scn = self.APV_SystSettings.sceneDict

        self.singleRow_length_x = float()
        self.singleRow_length_y = float()
        # footprint dimensions = dimensions of a vertical projection to ground
        self.singleRow_footprint_x = float()
        self.singleRow_footprint_y = float()

        self.allRows_footprint_x = float()
        self.allRows_footprint_y = float()

        self.x_field = int()
        self.y_field = int()

        # shifts from apv- and groundscan_field-center towards origin (x=y=0):
        # for azimuth = 0:
        self.center_offset_azi0_x = float()
        self.center_offset_azi0_y = float()
        # for azimuth from scenedict:
        self.center_offset_x = float()
        self.center_offset_y = float()

        # south west corners of all modules at
        # azimuth = 0, used as mounting structure anchor later:
        self.sw_modCorner_azi0_x = float()
        self.sw_modCorner_azi0_y = float()

        self._set_init_variables()

    def _set_init_variables(self):

        self.singleRow_length_x = (
            self.mod['x']*self.scn['nMods']
            + self.mod['xgap']*(self.scn['nMods']-1)
        )

        self.singleRow_length_y = (
            self.mod['y']*self.mod['numpanels']
            + self.mod['ygap']*(self.mod['numpanels']-1)
        )

        # for now no tilt in x
        self.singleRow_footprint_x = self.singleRow_length_x

        self.singleRow_footprint_y = self.singleRow_length_y*np.cos(
            self.scn['tilt']*np.pi/180)

        # for now no array translation in x
        self.allRows_footprint_x = self.singleRow_footprint_x

        # pitch is from row center to row center. Therefore on each side
        # only half of the singleRow_footprint needs to be added
        self.allRows_footprint_y = (
            self.singleRow_footprint_y+self.scn['pitch']*(self.scn['nRows']-1)
        )

        # ### ground scan dimensions (x_field, y_field)
        # margins:
        m_x = self.APV_SystSettings.ground_scan_margin_x
        m_y = self.APV_SystSettings.ground_scan_margin_y

        # field:
        x_field0 = self.allRows_footprint_x + 2*m_x
        y_field0 = self.allRows_footprint_y + 2*m_y

        # make it larger if not azimuth = 0 or 180 to cover footprint within
        # scan field aligned to north and parallel to x and y axes:
        azi_rad = self.scn['azimuth']*np.pi/180
        x_field = abs(np.sin(azi_rad))*y_field0 + abs(np.cos(azi_rad))*x_field0
        # switch cos and sin for y
        y_field = abs(np.cos(azi_rad))*y_field0 + abs(np.sin(azi_rad))*x_field0

        # round up (ceiling)
        if self.APV_SystSettings.round_up_field_dimensions:
            x_field = np.ceil(x_field)
            y_field = np.ceil(y_field)

        # write to self attribute
        self.x_field = x_field
        self.y_field = y_field

        # ## center offsets
        self.center_offset_azi0_x = 0
        self.center_offset_azi0_y = 0

        if self.scn['nMods'] % 2 == 0:  # even
            self.center_offset_azi0_x = (self.mod['x']+self.mod['xgap'])/2
        if self.scn['nRows'] % 2 == 0:  # even
            self.center_offset_azi0_y = self.scn['pitch']/2

        self.center_offset_x = -(
            self.center_offset_azi0_x*np.cos(azi_rad)
            + self.center_offset_azi0_y*np.sin(azi_rad)
        )
        self.center_offset_y = -(
            self.center_offset_azi0_y*np.cos(azi_rad)
            - self.center_offset_azi0_x*np.sin(azi_rad)
        )

        # south west corners of the modules with azimuth = 0
        self.sw_modCorner_azi0_x = (
            -self.allRows_footprint_x/2 + self.center_offset_azi0_x)

        self.sw_modCorner_azi0_y = (
            -self.allRows_footprint_y/2 + self.center_offset_azi0_y)

        # south west corners of the ground scan area
        s_x = self.APV_SystSettings.ground_scan_shift_x
        s_y = self.APV_SystSettings.ground_scan_shift_y

        self.sw_corner_scan_x = -self.x_field/2 + self.center_offset_x + s_x
        self.sw_corner_scan_y = -self.y_field/2 + self.center_offset_y + s_y

    def framed_single_axes_mount(self) -> str:
        """Creates Aluminum posts and mounting structure
        for azimuth = 0,
        correct rotation is done later
        """

        material = 'Metal_Aluminum_Anodized'

        s_beam = 0.15  # beam thickness
        d_beam = 0.5  # beam distance
        s_post = self.APV_SystSettings.s_post  # post thickness
        n_post_x = self.APV_SystSettings.n_post_x

        h_post = self.scn["hub_height"] + 0.2  # post height

        x_length = self.allRows_footprint_x + 4*s_post
        clone_distance_x = x_length/(n_post_x-1)
        y_length = self.allRows_footprint_y-self.singleRow_footprint_y

        x_start = self.sw_modCorner_azi0_x - 2*s_post
        y_start = self.sw_modCorner_azi0_y + self.singleRow_footprint_y/2

        # create posts
        text = (f'!genbox {material} post {s_post} {s_post} {h_post}'
                f' | xform -t {x_start} {y_start} 0 \
                -a {n_post_x} -t {clone_distance_x} 0 0 \
                -a {self.scn["nRows"]} -t 0 {self.scn["pitch"]} 0 '
                )
        # create horizontal beams in y direction
        text += (f'\n!genbox {material} post {s_beam} {y_length} {s_beam} \
            | xform -t {x_start} {y_start} {h_post - s_beam - 0.4} \
            -a {n_post_x} -t {clone_distance_x} 0 0 -a 2 -t 0 0 {-d_beam} ')
        # create horizontal beams in x direction
        text += (f'\n!genbox {material} post {x_length} {s_beam} {s_beam} \
                | xform -t {x_start} {y_start} {h_post - s_beam - 0.2} \
                -a {self.scn["nRows"]} -t 0 {self.scn["pitch"]} 0 \
                -a 2 -t 0 0 {-d_beam} '
                 )
        return text

    def groundscan_area(self) -> str:
        text = (
            f'!genbox grass field {self.x_field} {self.y_field} 0.00001'
            f' | xform -t {self.sw_corner_scan_x} {self.sw_corner_scan_y} 0'
        )

        if self.debug_mode:
            text += (
                # mark origin
                f'\n!genbox black post {0.5} {0.5} 10'
                f'\n!genbox white_EPDM post {0.2} {0.2} 10'
                # mark field center
                f'\n!genbox black post {0.3} {0.3} 8 | xform '
                f'-t {self.center_offset_x} {self.center_offset_y} 0'
                # mark system edge
                f'\n!genbox black post {0.2} {0.2} 8 | xform '
                f'-t {self.sw_corner_scan_x} {self.sw_corner_scan_y} 0'
            )

        return text

    def declined_tables_mount(self, add_glass_box=False) -> str:
        """
        tilted along y
        origin x: x-center of the "int((nMods+1)/2)"ths module
        origin y: nRow uneven: y-center of the center row
                nRow even: y_center of the the row south to the system center
        """

        scn = self.scn

        # define these: ####
        inner_table_post_distance_y = 3.4  # *table_footprint_y/4.8296
        # table_footprint_y/4.8296 = ca. 1 for given setup
        post_count_x = 3  # in x (east -> west for azi=180)
        material = 'Metal_Aluminum_Anodized'
        s_post = 0.15  # post thickness
        # #########

        # post starts in y:
        lower_post_start_y = self.sw_modCorner_azi0_y + (
            self.singleRow_footprint_y - inner_table_post_distance_y)/2

        higher_post_start_y = lower_post_start_y + inner_table_post_distance_y

        height_shift = inner_table_post_distance_y*np.sin(
            scn['tilt']*np.pi/180)/2
        h_lower_post = scn["hub_height"] - height_shift  # lower post height
        h_higher_post = scn["hub_height"] + height_shift  # higher post height

        post_distance_x = self.singleRow_footprint_x / (post_count_x-1)
        # create lower posts
        text = (
            f'! genbox {material} post {s_post} {s_post} {h_lower_post}'
            f' | xform -t {self.sw_modCorner_azi0_x} {lower_post_start_y} 0 '
            f'-a {post_count_x} -t {post_distance_x} 0 0 '
            f'-a {scn["nRows"]} -t 0 {scn["pitch"]} 0 ')

        # create lower posts
        text += (
            f'\n! genbox {material} post {s_post} {s_post} {h_higher_post}'
            f' | xform -t {self.sw_modCorner_azi0_x} {higher_post_start_y} 0 '
            f'-a {post_count_x} -t {post_distance_x} 0 0 '
            f'-a {scn["nRows"]} -t 0 {scn["pitch"]} 0 ')

        if add_glass_box:
            t_y = (self.sw_modCorner_azi0_y + self.allRows_footprint_y
                   + self.APV_SystSettings.glass_box_to_APV_distance)
            # variable cannot be found because not in default()
            # but in declined tables apv system settings

            t_x = self.allRows_footprint_x
            text += (f'\n! genbox stock_glass glass_wall {t_x} 0.005 5'
                     f' | xform -t {self.sw_modCorner_azi0_x} {t_y} 0')

        return text


def checked_module(APV_SystSettings: APV_SystSettings) -> str:
    c = APV_SystSettings.cellLevelModuleParams
    m = APV_SystSettings.moduleDict

    # copied from br.main.RadianceObj.makeModule() and modified:
    x = c['numcellsx']*c['xcell'] + (c['numcellsx']-1)*c['xcellgap']
    y = c['numcellsy']*c['ycell'] + (c['numcellsy']-1)*c['ycellgap']

    # center cell -
    if c['numcellsx'] % 2 == 0:
        cc = c['xcell']/2.0
        print(
            "Module was shifted by {} in X to avoid sensors on air".format(
                cc))

    material = 'black'
    # first PV cell
    text = '! genbox {} cellPVmodule {} {} {} | '.format(
        material, c['xcell'], c['ycell'], 0.02  # module thickness
    )
    # shift cell to lower corner
    text += 'xform -t {} {} {} '.format(
        -x/2.0 + cc,
        (-y*m['numpanels'] / 2.0)-(m['ygap'] * (m['numpanels']-1) / 2.0),
        0  # offset from axis
    )

    # def copypaste_radiance_geometry(
    # number_of_copies, displacement_x, displacement_y)

    # checker board
    text += '-a {} -t {} 0 0 '.format(
        int(c['numcellsx']/2),
        (2 * c['xcell'] + c['xcellgap']))

    text += '-a {} -t 0 {} 0 '.format(
        c['numcellsy']/2,
        (2 * c['ycell'] + c['ycellgap']))

    text += '-a {} -t {} {} 0 '.format(
        2,
        c['xcell'] + c['xcellgap'],
        c['ycell'] + c['ycellgap'])

    # copy module in y direction
    text += '-a {} -t 0 {} 0'.format(m['numpanels'], y+m['ygap'])

    # OPACITY CALCULATION
    packagingfactor = np.round(
        (c['xcell']*c['ycell']*c['numcellsx']*c['numcellsy'])/(x*y), 2
    )
    print("This is a Cell-Level detailed module with Packaging " +
          "Factor of {} %".format(packagingfactor))

    return text


def make_text_EW(APV_SystSettings: APV_SystSettings) -> str:
    """creates the needed text needed in makemodule() to create E-W.
    Azimuth angle must be 90! and number of panels must be 2!

    Args:
        APV_SystSettings:
        name ([str]): module_type
        moduleDict ([dict]): inherited from br_setup and defined in settings.py
        sceneDict  ([dict]): inherited from br_setup and defined in settings.py

    Returns:
        text [str]: [text to rotate second panel to create E-W (270 - 90)]
    """
    sDict = APV_SystSettings.sceneDict
    mDict = APV_SystSettings.moduleDict
    name = 'EWstd'
    z = 0.02
    Ny = mDict['numpanels']  # currently must be 2
    offsetfromaxis = 0.01
    tranistion_y = (-mDict['y']*Ny/2.0)-(mDict['ygap']*(Ny-1)/2.0)
    rotation_angle = 2*(90 - sDict['tilt']) + 180

    text = '! genbox black {} {} {} {} '.format(
        name, mDict['x'], mDict['y'], z)
    text += '| xform -t {} {} {} '.format(
        -mDict['x']/2.0, (-mDict['y']*Ny/2.0)-(mDict['ygap']*(Ny-1)/2.0),
        offsetfromaxis)
    text += '-a {} -t 0 {} 0 -rx {}'.format(
        Ny, mDict['y']+mDict['ygap'], rotation_angle)

    return text


def cell_level_EW_fixed(APV_SystSettings: APV_SystSettings) -> str:
    """creates needed text needed in makemodule() to create cell-level E-W.
    Azimuth angle must be 90! and number of panels must be 2!

    Args:
        APV_SystSettings:
        name ([str]): module_type
        moduleDict ([dict]): inherited from br_setup and defined in settings.py
        sceneDict  ([dict]): inherited from br_setup and defined in settings.py

    Returns:
        text [str]: [text to rotate second panel to create E-W (270 - 90)]
    """
    sc = APV_SystSettings.sceneDict
    m = APV_SystSettings.moduleDict

    z = 0.02
    Ny = m['numpanels']  # currently must be 2
    offsetfromaxis = 0.01
    rotation_angle = 2*(90 - sc['tilt']) + 180

    c = APV_SystSettings.cellLevelModuleParams
    x = c['numcellsx']*c['xcell'] + (c['numcellsx']-1)*c['xcellgap']
    y = c['numcellsy']*c['ycell'] + (c['numcellsy']-1)*c['ycellgap']
    material = 'black'
    # center cell -
    if c['numcellsx'] % 2 == 0:
        cc = c['xcell']/2.0
        print("Module was shifted by {} in X to\
              avoid sensors on air".format(cc))

    text = '! genbox {} cellPVmodule {} {} {} | '.format(material, c['xcell'],
                                                         c['ycell'], z)
    text += 'xform -t {} {} {} '.format(-x/2.0 + cc,
                                        (-y*Ny / 2.0) -
                                        (m['ygap']*(Ny-1) / 2.0),
                                        offsetfromaxis)
    text += '-a {} -t {} 0 0 '.format(c['numcellsx'], c['xcell'] +
                                      c['xcellgap'])
    text += '-a {} -t 0 {} 0 '.format(c['numcellsy'], c['ycell'] +
                                      c['ycellgap'])
    text += '-a {} -t 0 {} 0 -rx {}'.format(Ny, y+m['ygap'], rotation_angle)

    # OPACITY CALCULATION
    packagingfactor = np.round((c['xcell']*c['ycell']*c['numcellsx'] *
                                c['numcellsy'])/(x*y), 2)
    print("This is a Cell-Level detailed module with Packaging " +
          "Factor of {} %".format(packagingfactor))

    return text


""" def add_box_to_radiance_text(
    text=str(),
    material, name,
    size_x, size_y, size_z,
    position_x, position_y, position_z,
    copies_x=1, copies_y=1, copies_z=1,
    distance_between, array_distance_y, array_distance_z
    array_distance_x
    )->str:
        text += (f'\n! genbox {material} post {x_length} {s_beam} {s_beam} \
            | xform  -t {x_start} {y_start} {h_post - s_beam - 0.2} \
            -a 3 -t 0 {sDict["pitch"]} 0 -a 2 -t 0 0 {-d_beam} ')

    return text

def array_copy_ """
