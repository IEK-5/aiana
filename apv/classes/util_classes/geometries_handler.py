"""documentation links

    GENBOX (create a box with a certain size)
    https://floyd.lbl.gov/radiance/man_html/genbox.1.html

    GENREV (to create tubes, rings, donats, etc.)
    https://floyd.lbl.gov/radiance/man_html/genrev.1.html

    XFORM (translate, rotate, make arrays):
    https://floyd.lbl.gov/radiance/man_html/xform.1.html

    """

import numpy as np
from apv.classes.util_classes.settings_grouper import Settings


class GeometriesHandler:
    """
    to create the radiance text string for the oct file builder

    azimuth is handled here completely as being zero with x=y=0 in bottom left
    (south-west-corner for azimuth = 180° = default = south-oriented)

    real azimuth will be handled by rotating the sky in br._wrapper.create_sky()
    """
    # BR_radObj:

    singleRow_length_x: float
    singleRow_length_y: float
    # footprint dimensions = dimensions of a vertical projection to ground
    singleRow_footprint_x: float
    singleRow_footprint_y: float

    allRows_footprint_x: float
    allRows_footprint_y: float

    scan_length_x: int  # lengths of the groundscan area in x direction
    scan_length_y: int

    # shifts from apv- and groundscan_field-center towards origin (x=y=0):
    center_offset_x: float
    center_offset_y: float

    # south west corners of all modules used later
    # as mounting structure anchor/"array start":
    scan_area_anchor_x: float
    scan_area_anchor_y: float

    clone_distance_x: float
    post_start_x: float
    post_distance_x: float

    ygrid: list[int]
    groundscan: dict
    # frontscan: dict
    # backscan: dict

    def __init__(self, settings: Settings, debug_mode=False):
        self.settings = settings
        self.debug_mode = debug_mode
        # short cuts:
        self.mod = settings.apv.moduleDict
        self.scn = settings.apv.sceneDict
        self.mount = settings.apv.mountingStructureDict

        self._adjust_settings()
        self._set_singleRow_lengths_and_footprints()
        self._set_scan_lengths_x_y()  # TODO rename to GroundScanLength_x_y ?
        self._set_APVSystCenter_to_origin_offsets()
        self._set_x_y_coordinates_of_modCorner_and_scanArea_anchors()
        self._set_y_grid_and_sensors()
        self._set_groundscan_dict()
        self._set_post_x_pos_respecting_cloning()

    def _adjust_settings(self):
        """adjust apv syst settings, e.g. add cell sizes"""

        mod_form = self.settings.apv.module_form
        print('\n##### ' + mod_form.replace('_', ' ')
              + ' simulation mode #####\n')

        # if simSettings.module_form == 'cell_level_checker_board':
        #     # for checkerboard on cell level calculate only one module
        #     # and enlarge module in y direction to have the same PV output
        #     simSettings.moduleDict['y'] *= 2
        c = self.settings.apv.cellLevelModuleParams

        if mod_form == 'EW_fixed' or mod_form == 'cell_level_EW_fixed':
            self.scn['azimuth'] = 90  # TODO check again
            # since change leading to sky rotation
            self.mod['numpanels'] = 2

        def get_cellSize(mod_size, num_cell, cell_gap):
            # formula derivation:
            # x = numcellsx * xcell + (numcellsx-1) * xcellgap
            # xcell = (x - (numcellsx-1)*xcellgap) / numcellsx
            cell_size = (mod_size - (num_cell-1)*cell_gap) / num_cell
            return cell_size

        c['xcell'] = get_cellSize(self.mod['x'], c['numcellsx'], c['xcellgap'])
        c['ycell'] = get_cellSize(self.mod['y'], c['numcellsy'], c['ycellgap'])

        if mod_form in ['cell_level', 'cell_level_EW_fixed',
                        'cell_level_checker_board']:
            if mod_form == 'cell_level_checker_board':
                factor = 2
            else:
                factor = 1
            packingfactor = np.round(
                c['xcell']*c['ycell']*c['numcellsx']*c['numcellsy']/(
                    factor*self.mod['x']*self.mod['y']), 2
            )
            print("This is a Cell-Level detailed module with Packaging "
                  + f"Factor of {packingfactor}.")

    def _set_singleRow_lengths_and_footprints(self):

        self.singleRow_length_x = self.mod['x']*self.scn['nMods'] \
            + self.mod['xgap']*(self.scn['nMods']-1)

        self.singleRow_length_y = self.mod['y']*self.mod['numpanels'] \
            + self.mod['ygap']*(self.mod['numpanels']-1)

        # footprints
        self.singleRow_footprint_x = self.singleRow_length_x  # no x-tilt yet
        self.singleRow_footprint_y = self.singleRow_length_y*np.cos(
            self.scn['tilt']*np.pi/180)

        # for now no array translation in x #TODO add clones here
        self.allRows_footprint_x = self.singleRow_footprint_x

        # pitch is from row center to row center. Therefore on each side
        # only half of the singleRow_footprint needs to be added
        self.allRows_footprint_y = (
            self.singleRow_footprint_y+self.scn['pitch']*(self.scn['nRows']-1)
        )

    def _set_post_x_pos_respecting_cloning(self):
        modPostDist = self.mount['module_to_post_distance_x']
        # array cloning distance in x (in y called 'pitch' by BR)
        self.clone_distance_x = self.singleRow_footprint_x + 2*modPostDist
        # post start and distance used for building mounting structure
        self.post_start_x = self.sw_modCorner_x - modPostDist
        self.post_distance_x = self.clone_distance_x/(self.mount['n_post_x']-1)

    def _set_scan_lengths_x_y(self):
        """ground scan dimensions (old name: x_field, y_field)"""

        if self.mount['module_to_post_distance_x'] > 0:
            extra_x = self.mount['post_thickness']
        else:
            extra_x = 0

        self.scan_length_x = self.allRows_footprint_x \
            + 2*self.settings.apv.ground_scan_margin_x \
            + self.mount['module_to_post_distance_x'] \
            + extra_x

        self.scan_length_y = self.allRows_footprint_y \
            + 2*self.settings.apv.ground_scan_margin_y

        # round up (ceiling)
        if self.settings.apv.round_up_field_dimensions:
            self.scan_length_x = np.ceil(self.scan_length_x)
            self.scan_length_y = np.ceil(self.scan_length_y)

    def _set_APVSystCenter_to_origin_offsets(self):
        self.center_offset_x = 0
        self.center_offset_y = 0

        if self.scn['nMods'] % 2 == 0:  # even
            self.center_offset_x = (self.mod['x']+self.mod['xgap'])/2
        if self.scn['nRows'] % 2 == 0:  # even
            self.center_offset_y = self.scn['pitch']/2

    def _set_x_y_coordinates_of_modCorner_and_scanArea_anchors(self):
        # south west corners before rotation
        self.sw_modCorner_x = (
            -self.allRows_footprint_x/2 + self.center_offset_x)
        self.sw_modCorner_y = (
            -self.allRows_footprint_y/2 + self.center_offset_y)

        # south west corners of the ground scan area
        self.scan_area_anchor_x = -self.scan_length_x/2 + self.center_offset_x \
            + self.settings.apv.ground_scan_shift_x
        self.scan_area_anchor_y = -self.scan_length_y/2 + self.center_offset_y \
            + self.settings.apv.ground_scan_shift_y

    def get_rad_txt_for_cloning_the_apv_system(self) -> str:
        """Usefull for periodic boundary conditions.
        Returns:
            (str): radiance text
        """

        shift_x_array_start = \
            -self.settings.apv.n_apv_system_clones_in_negative_x \
            * self.clone_distance_x

        # total count n of cloned system segments
        # (segment = structure + modules without a gap in x direction)
        n_system_segments_x = self.settings.apv.n_apv_system_clones_in_x \
            + 1 + self.settings.apv.n_apv_system_clones_in_negative_x

        if n_system_segments_x > 1:
            return (f'!xform -t {shift_x_array_start} 0 0 '
                    f'-a {n_system_segments_x} -t {self.clone_distance_x} 0 0 '
                    )
        else:
            return '!xform '

    def framed_single_axes_mount(self) -> str:
        """Creates Aluminum posts and mounting structure
        for azimuth = 0,
        correct rotation is done later
        """

        material = 'Metal_Aluminum_Anodized'

        s_beam = 0.15  # beam thickness
        d_beam = 0.5  # beam distance

        beamlength_x = self.post_distance_x

        if self.settings.apv.enlarge_beams_for_periodic_shadows:
            beamlength_x = self.allRows_footprint_x * 1.2
            # to get periodic shadows in summer sunrise and set
            beamlength_y = self.scn['pitch']*(self.scn['nRows']-0.4)
        else:
            beamlength_y = self.scn['pitch']*(self.scn['nRows']-1)

        y_start = self.sw_modCorner_y + self.singleRow_footprint_y/2
        h_post = self.scn["hub_height"] + 0.2

        # create posts
        text = self.post_array(h_post, y_start)

        # create horizontal beams in y direction
        if self.scn['nRows'] > 1:
            text += (
                f'\n!genbox {material} post {s_beam} {beamlength_y} {s_beam} \
                | xform -t {self.post_start_x} {y_start} {h_post-s_beam-0.4} \
                -a {self.mount["n_post_x"]} -t {self.post_distance_x} \
                0 0 -a 2 -t 0 0 {-d_beam} '
            )
        # create horizontal beams in x direction
        text += (
            f'\n!genbox {material} post {beamlength_x} {s_beam} {s_beam} \
            | xform -t {self.post_start_x} {y_start} {h_post - s_beam - 0.2} \
            -a {self.scn["nRows"]} -t 0 {self.scn["pitch"]} 0 \
            -a 2 -t 0 0 {-d_beam} '
        )
        return text

    def _set_y_grid_and_sensors(self):
        self.ygrid: list[float] = np.arange(
            self.scan_area_anchor_y,
            (self.scan_area_anchor_y + self.scan_length_y
             + self.settings.sim.spatial_resolution),
            self.settings.sim.spatial_resolution)

        self.sensors_x = int(
            self.scan_length_x / self.settings.sim.spatial_resolution)+1

    def _set_groundscan_dict(self):
        """
        groundscan (dict): dictionary containing the XYZ-start and
        -increments values for a bifacial_radiance linescan.
        It describes where the virtual ray tracing sensors are placed.
        The origin (x=0, y=0) of the PV facility is in its center.
        """

        sx_xinc = self.settings.sim.spatial_resolution
        self.groundscan = {
            'xstart':  self.scan_area_anchor_x,  # bottom left for azimuth 180
            'ystart': self.scan_area_anchor_y,
            # ystart will be set by looping ygrid for multiprocessing
            'zstart': 0.001,  # 0.05,
            'xinc': 0, 'yinc': 0, 'zinc': 0,
            'sx_xinc': sx_xinc, 'sx_yinc': 0, 'sx_zinc': 0,
            # NOTE Sensor x-coordinate = xstart + iy*xinc + ix*sx_xinc,
            # whereby iy und ix are looped over range(Ny) and range(Nx)
            'Nx': self.sensors_x, 'Ny': 1, 'Nz': 1,
            'orient': '0 0 -1'
        }

        print(f'\n sensor grid:\nx: {self.sensors_x}, y: {len(self.ygrid)}, '
              f'total: {self.sensors_x * len(self.ygrid)}')

    # =========================================================================
    # =============================== RAD TEXTS: ==============================
    # =========================================================================

    def groundscan_area_and_sensors(self) -> str:
        g = self.groundscan
        # ground scan area
        text = (
            f'!genbox grass field {self.scan_length_x} {self.scan_length_y} 0.00001'
            f' | xform -t {g["xstart"]} {g["ystart"]} 0'
        )
        # sensors
        s = 0.05
        text += (
            f'\n!genbox red sensor {s} {s} {s/2} '
            f'| xform -t {g["xstart"]} {g["ystart"]} 0 '
            f'-a {self.sensors_x} -t {g["sx_xinc"]} 0 0 '
            f'-a {len(self.ygrid)} -t 0 {g["sx_xinc"]} 0'  # x- and y-inc equal
        )

        if self.debug_mode:
            rz = 180 - self.scn['azimuth']
            text += (
                # mark origin
                f'\n!genbox black post 0.5 0.5 10'
                f'\n!genbox white_EPDM post 0.2 0.2 10'

                # mark field center
                f'\n!genbox black post {0.3} {0.3} 8 '
                f'| xform -t {self.center_offset_x} {self.center_offset_y} 0'
                # mark system edge
                f'\n!genbox black post {0.2} {0.2} 8 '
                f'| xform -t {g["xstart"]} {g["ystart"]} 0'
            )
        return text

    def declined_tables_mount(self) -> str:
        """
        tilted along y
        origin x: x-center of the "int((nMods+1)/2)"ths module
        origin y: nRow uneven: y-center of the center row
                nRow even: y_center of the the row south to the system center
        """
        # overwrite for Morschenich special case
        self.post_distance_x = 4
        self.post_start_x = -20+self.center_offset_x
        post_dist_y = self.mount['inner_table_post_distance_y']

        # post starts in y:
        middle_post_start_y = self.sw_modCorner_y+self.singleRow_footprint_y/2
        lower_post_start_y = middle_post_start_y-post_dist_y
        higher_post_start_y = middle_post_start_y+post_dist_y

        height_shift = post_dist_y*np.sin(
            self.scn['tilt']*np.pi/180)/2

        # create lower posts
        text = self.post_array(
            self.scn["hub_height"] - height_shift,  # lower post height
            lower_post_start_y)
        # middle posts
        text += '\n'+self.post_array(
            self.scn["hub_height"], middle_post_start_y)
        # add higher posts
        text += '\n'+self.post_array(
            self.scn["hub_height"] + height_shift,  # higher post height
            higher_post_start_y)

        if self.settings.apv.add_glass_box:
            t_y = (self.sw_modCorner_y + self.allRows_footprint_y
                   + self.settings.apv.glass_box_to_APV_distance)
            # variable cannot be found because not in default()
            # but in declined tables apv system settings

            t_x = self.allRows_footprint_x
            text += (f'\n!genbox stock_glass glass_wall {t_x} 0.005 5'
                     f' | xform -t {self.sw_modCorner_x} {t_y} 0')

        if self.settings.apv.add_airrails:

            n_rails = 8
            s_rail = 0.08
            s = self.mount['post_thickness']
            l_x = 20*2
            # inclined beams in parallel to y
            y_start = self.sw_modCorner_y+self.singleRow_length_y
            text += (
                f'\n!genbox {self.mount["material"]} post {s} 4.8 {s}'
                f' | xform -rx -14 -t {self.post_start_x} {y_start} 3.8 '
                f'-a {self.mount["n_post_x"]*2-1} -t 2 0 0 '
                f'-a {self.scn["nRows"]-1} -t 0 {self.scn["pitch"]} 0 '
            )
            # streight rails in steps parallel to x
            y_start += 0.25
            text += (
                f'\n!genbox {self.mount["material"]} post {l_x} {s_rail} {s_rail}'
                f' | xform -rx -14 -t {self.post_start_x} {y_start} 3.84 '
                f'-a {n_rails} -t 0 0.5 -0.125 '
                f'-a {self.scn["nRows"]-1} -t 0 {self.scn["pitch"]} 0 '
            )
        return text

    def post_array(
            self, post_height: float, post_start_y: float) -> str:
        """ creats an array of posts for each row using
        APV_Systsettings.mountingStructureDict """

        s = self.mount['post_thickness']
        text = (
            f'!genbox {self.mount["material"]} post {s} {s} {post_height}'
            f' | xform -t {self.post_start_x} {post_start_y} 0 '
            f'-a {self.mount["n_post_x"]} -t {self.post_distance_x} 0 0 '
            f'-a {self.scn["nRows"]} -t 0 {self.scn["pitch"]} 0 '
        )
        return text

    def make_checked_module_text(self) -> str:

        mod = self.mod
        c = self.settings.apv.cellLevelModuleParams

        # copied from br.main.RadianceObj.makeModule() and modified:
        x = c['numcellsx']*c['xcell']+(c['numcellsx']-1)*c['xcellgap']
        y = c['numcellsy']*c['ycell']+(c['numcellsy']-1)*c['ycellgap']

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
            (-y*mod['numpanels']/2.0)-(mod['ygap']*(mod['numpanels']-1) / 2.0),
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
        text += '-a {} -t 0 {} 0'.format(mod['numpanels'], y+mod['ygap'])

        return text

    def make_EW_module_text(self) -> str:
        """creates the needed text needed in makemodule() to create E-W.
        Azimuth angle must be 90! and number of panels must be 2!

        Returns:
            text [str]: [text to rotate second panel to create E-W (270 - 90)]
        """

        mod = self.mod

        name = 'EWstd'
        z = 0.02
        Ny = mod['numpanels']  # currently must be 2
        offsetfromaxis = 0.01
        transition_y = (-mod['y']*Ny/2.0)-(mod['ygap']*(Ny-1)/2.0)
        rotation_angle = 2*(90 - self.scn['tilt']) + 180

        text = '! genbox black {} {} {} {} '.format(
            name, mod['x'], mod['y'], z)
        text += '| xform -t {} {} {} '.format(
            -mod['x']/2.0, transition_y, offsetfromaxis)
        text += '-a {} -t 0 {} 0 -rx {}'.format(
            Ny, mod['y']+mod['ygap'], rotation_angle)

        return text

    def make_cell_level_EW_module_text(self) -> str:
        """creates needed text needed in makemodule() to create cell-level E-W.
        Azimuth angle must be 90! and number of panels must be 2!

        Returns:
            text [str]: [text to rotate second panel to create E-W (270 - 90)]
        """

        z = 0.02
        Ny = self.mod['numpanels']  # currently must be 2
        ygap = self.mod['ygap']

        offsetfromaxis = 0.01
        rotation_angle = 2*(90 - self.scn['tilt']) + 180

        c = self.settings.apv.cellLevelModuleParams
        # copied from br.main.RadianceObj.makeModule() and modified:
        x = c['numcellsx']*c['xcell']+(c['numcellsx']-1)*c['xcellgap']
        y = c['numcellsy']*c['ycell'] + (c['numcellsy']-1)*c['ycellgap']
        material = 'black'
        # center cell -
        if c['numcellsx'] % 2 == 0:
            cc = c['xcell']/2.0
            print("Module was shifted by {} in X to\
                avoid sensors on air".format(cc))

        text = '! genbox {} cellPVmodule {} {} {} | '.format(
            material, c['xcell'], c['ycell'], z)
        text += 'xform -t {} {} {} '.format(-x/2.0 + cc,
                                            (-y*Ny / 2.0) -
                                            (ygap*(Ny-1) / 2.0),
                                            offsetfromaxis)
        text += '-a {} -t {} 0 0 '.format(c['numcellsx'], c['xcell'] +
                                          c['xcellgap'])
        text += '-a {} -t 0 {} 0 '.format(c['numcellsy'], c['ycell'] +
                                          c['ycellgap'])
        text += '-a {} -t 0 {} 0s -rx {}'.format(Ny, y+ygap, rotation_angle)

        return text

    def north_arrow(self) -> str:
        text = (
            f'\n!genbox black peak 1 1 0.001 | xform -t -0.5 -0.5 0 -rz 45'
            f'\n!genbox black base 1.4 1.4 0.001 | xform -t -0.7 -1.4 0'
        )
        return text
        # f'| genbox black post 0.5 2 0.001 '
        # f'| xform -t -0.5 -0.5 0 -rz {rz+angle} -t 10 {10+shift} 0'
        # )

        '''
        if settings.apv.n_apv_system_clones_in_x > 1 \
                or settings.apv.n_apv_system_clones_in_negative_x > 1:
            """ TODO cleaner code and slight speed optimization:
        Return concat of matfiles, radfiles and skyfiles

        filelist = self.radObj.materialfiles + self.radObj.skyfiles \
            + radfiles << - ersetzen mit eigener liste ohne erstes set
        um eigene liste zu erstellen, makeCustomobject und appendtoscene
        in eine eigene Methode zusammenführen mit besserer Namensgebung.

        """

            # was hier passiert: um alle module kopieren zu können, muss
            # module + scene erstellung in einem schritt erfolgen, damit ein
            # file anschließend als ganzes (ohne interne file weiterleitung)
            # kopiert werden kann. Dazu nehme ich die rad_text
            # aus br und modifiziere sie.
            modules_text = (
                self.radObj.moduleDict['text']  # module text
                # (only "numpanels" considered)
                + self.scene.text.replace(  # all modules in first set
                    '!xform', '|xform').replace(
                    f' objects\\{self.settings.apv.module_name}.rad', ''))

            self.radObj.appendtoScene(
                radfile=self.scene.radfiles,
                customObject=self.radObj.makeCustomObject(
                    'copied_modules', modules_text),
                # cloning all modules from first set into all sets
                text=self.geomObj.get_customObject_cloning_rad_txt(
                    settings.apv)
            )

        # add ground scan area visualization to the radObj without rotation

            """
        ground_rad_text = ghObj.groundscan_area()

        self.radObj.appendtoScene(  # '\n' + text + ' ' + customObject
            radfile=self.scene.radfiles,
            customObject=self.radObj.makeCustomObject(
                'scan_area', ground_rad_text),
            text='!xform '  # with text = '' (default) it does not work!
            # all scene objects are stored in
            # bifacial_radiance_files/objects/... e.g.
            # SUNFARMING_C_3.81425_rtr_10.00000_tilt_20.00000_10modsx3...
            # within this file different custom .rad files are concatenated
            # by !xform object/customObjectName.rad
        )
        """
        '''


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
