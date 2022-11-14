
from aiana.classes.util_classes.settings_handler import Settings
import numpy as np


class GeomBasics:
    """
    azimuth is handled here completely as being zero with x=y=0 in bottom left
    (south-west-corner for azimuth = 180° = default = south-oriented)

    real azimuth will be handled by rotating the sky in br._wrapper.create_sky()

    documentation links

    GENBOX (create a box with a certain size)
    https://floyd.lbl.gov/radiance/man_html/genbox.1.html

    GENREV (to create tubes, rings, donats, etc.)
    https://floyd.lbl.gov/radiance/man_html/genrev.1.html

    XFORM (translate, rotate, make arrays):
    https://floyd.lbl.gov/radiance/man_html/xform.1.html

    """
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
    ground_lineScan: dict
    # frontscan: dict
    # backscan: dict

    def __init__(self, settings: Settings, debug_mode=False):
        """has it's own debug_mode so it can be set seperately.
        # set True for and geometric markes (high pillars) of origin,
        # apv system center, and -edge
        """
        self.settings = settings
        self.debug_mode = debug_mode
        # short cuts:
        self.mod = settings.apv.moduleDict
        self.scn = settings.apv.sceneDict
        self.mount = settings.apv.mountingStructureDict

        self._add_cell_sizes()
        self._print_packingFactor()
        self._set_singleRow_lengths_and_footprints()
        self._set_scan_lengths_x_y()  # TODO rename to GroundScanLength_x_y ?
        self._set_APVSystCenter_to_origin_offsets()
        self._set_x_y_coordinates_of_modCorner_and_scanArea_anchors()
        self._set_y_grid_and_sensors()
        self._set_groundscan_dicts()
        self._set_post_x_pos_respecting_cloning()

    def _add_cell_sizes(self):
        """adds cell sizes to the self.settings.apv.cellLevelModuleParams
        dictionary"""
        def calc_cSize(
                mod_size: float, num_cell: int, cell_gap: float) -> float:
            # formula derivation:
            # x = numcellsx * xcell + (numcellsx-1) * xcellgap
            # xcell = (x - (numcellsx-1)*xcellgap) / numcellsx
            cell_size = (mod_size - (num_cell-1)*cell_gap) / num_cell
            return cell_size

        c = self.settings.apv.cellLevelModuleParams
        c['xcell'] = calc_cSize(self.mod['x'], c['numcellsx'], c['xcellgap'])
        c['ycell'] = calc_cSize(self.mod['y'], c['numcellsy'], c['ycellgap'])

    def _print_packingFactor(self):
        c = self.settings.apv.cellLevelModuleParams
        mod_form = self.settings.apv.module_form
        if mod_form in ['cell_gaps', 'checker_board']:
            if mod_form == 'checker_board':
                factor = 2
            else:
                factor = 1
            packingfactor = np.round(
                c['xcell']*c['ycell']*c['numcellsx']*c['numcellsy']/(
                    factor*self.mod['x']*self.mod['y']), 2
            )
            print("This is a celllevel-detailed module with a packaging "
                  + f"factor of {packingfactor}.")

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
        modToPostDist_x = self.mount['module_to_post_distance_x']
        # array cloning distance in x (in y called 'pitch' by BR)
        self.clone_distance_x = self.singleRow_footprint_x + 2*modToPostDist_x
        # post start and distance used for building mounting structure
        self.post_start_x = self.sw_modCorner_x - modToPostDist_x \
            - self.mount['post_thickness_y']/2

        if self.mount['post_distance_x'] == "auto":
            self.post_distance_x = self.clone_distance_x/(
                self.mount['n_post_x']-1)
        else:
            self.post_distance_x = self.mount['post_distance_x']

    def _set_scan_lengths_x_y(self):
        """ground scan dimensions (old name: x_field, y_field)"""
        self.scan_length_x = self.allRows_footprint_x \
            + 2*self.settings.apv.gScanAreaDict['ground_scan_margin_x'] \
            + 2*self.mount['module_to_post_distance_x'] \

        self.scan_length_y = self.allRows_footprint_y \
            + 2*self.settings.apv.gScanAreaDict['ground_scan_margin_y']

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
            + self.settings.apv.gScanAreaDict['ground_scan_shift_x']
        self.scan_area_anchor_y = -self.scan_length_y/2 + self.center_offset_y \
            + self.settings.apv.gScanAreaDict['ground_scan_shift_y']

    def _set_y_grid_and_sensors(self):
        self.ygrid: list[float] = np.arange(
            self.scan_area_anchor_y,  # start
            (self.scan_area_anchor_y + self.scan_length_y
             + self.settings.sim.spatial_resolution*0.999),  # stop
            self.settings.sim.spatial_resolution)  # step

        self.n_sensors_x = \
            self.scan_length_x // self.settings.sim.spatial_resolution + 2
        # + 2 because + 1 for the one at x = 0 and another + 1 to hit the post
        # again or cover scan_length_x despite of rounding down with //

    def _set_groundscan_dicts(self):
        """
        groundscan (dict): dictionary containing the XYZ-start and
        -increments values for a bifacial_radiance linescan.
        It describes where the virtual ray tracing sensors are placed.
        The origin (x=0, y=0) of the PV facility is in its center.
        """

        xy_inc = self.settings.sim.spatial_resolution
        self.ground_lineScan = {
            'xstart':  self.scan_area_anchor_x,  # bottom left for azimuth 180
            'ystart': self.scan_area_anchor_y,
            # ystart will be set by looping ygrid for multiprocessing
            # 'zstart': 0.001,  # z shifted to sim settings scan_z_params
            'xinc': xy_inc, 'yinc': 0,  # 'zinc': 0,
            # 'sx_xinc': 0, 'sx_yinc': 0, 'sx_zinc': 0,
            'Nx': self.n_sensors_x, 'Ny': 1,  # 'Nz': 1,
            'orient': '0 0 -1'  # -1 to look downwards to the ground
            # NOTE radiance will return irradiation (?) on the surface beeing
            # hit by the vectors (rays) defined in linepts --> surface properties influence?
        }
        self.ground_lineScan.update(self.settings.sim.RadSensors_z_params)

        self.ground_areaScan = self.ground_lineScan.copy()
        self.ground_areaScan['yinc'] = xy_inc
        self.ground_areaScan['Ny'] = len(self.ygrid)

        print(f'\n=== sensor grid: x: {self.n_sensors_x}, y: {len(self.ygrid)}, '
              f'total: {self.n_sensors_x * len(self.ygrid)} ===')

    # =========================================================================
    # =============================== RAD TEXTS: ==============================
    # =========================================================================

    def groundscan_area(self) -> str:
        g = self.ground_areaScan
        m = self.settings.sim.spatial_resolution  # margin, otherwise
        # the edge will falsify the results
        l_x = self.scan_length_x+3/2*m
        l_y = self.scan_length_y+3/2*m
        l_z = 0.0001  # thickness
        z_shift = g["zstart"] -\
            self.settings.sim.RadSensors_to_scan_area_distance_z
        text = (
            f'!genbox grass field {l_x} {l_y} {l_z} '
            f'| xform -t {g["xstart"]-m/2} {g["ystart"]-m/2} {z_shift}'
        )
        return text

    def sensor_visualization(self) -> str:
        g = self.ground_areaScan

        # sensors rad text
        size = min(0.05, self.settings.sim.spatial_resolution/3)
        text = (
            f'\n!genbox red sensor {size} {size} {size} '
            f'| xform -t {g["xstart"]-size/2} {g["ystart"]-size/2} {g["zstart"]} '
            f'-a {g["Nx"]} -t {g["xinc"]} 0 0 '
            f'-a {g["Ny"]} -t 0 {g["yinc"]} 0'
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
        # does not work:
        #text += "\n!gensurf glass ball 'sin(PI*s)*cos(2*PI*t)' 'cos(PI*s)' 'sin(PI*s)*sin(2*PI*t)' 7 10"
        #text += "\n!genrev glass torus 'sin(2*PI*t)' '2+cos(2*PI*t)' 32"
        return text

    def north_arrow(self) -> str:
        text = (
            f'\n!genbox black peak 1 1 0.001 | xform -t -0.5 -0.5 0 -rz 45'
            f'\n!genbox black base 1.4 1.4 0.001 | xform -t -0.7 -1.4 0'
        )
        return text

    def framed_single_axes_mount(self) -> str:
        """Creates Aluminum posts and mounting structure
        for azimuth = 0,
        correct rotation is done later
        """

        s_beam = 0.15  # beam thickness
        d_beam = 0.5  # beam distance

        material = self.mount['material']
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
        text = self._post_array(h_post, y_start)

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
            | xform -t {self.post_start_x} {y_start} {h_post - s_beam - 0.25} \
            -a {self.scn["nRows"]} -t 0 {self.scn["pitch"]} 0 \
            -a 2 -t 0 0 {-d_beam} '
        )
        return text

    def inclined_tables(self) -> str:
        """
        tilted along y
        origin x: x-center of the "int((nMods+1)/2)"ths module
        origin y: nRow uneven: y-center of the center row
                nRow even: y_center of the the row south to the system center
        """

        post_dist_y = self.mount['inner_table_post_distance_y']

        # post starts in y:
        middle_post_start_y = self.sw_modCorner_y+self.singleRow_footprint_y/2
        lower_post_start_y = middle_post_start_y-post_dist_y
        higher_post_start_y = middle_post_start_y+post_dist_y

        height_shift = post_dist_y*np.tan(self.scn['tilt']*np.pi/180)

        # create lower posts
        text = self._post_array(
            self.scn["hub_height"] - height_shift,  # lower post height
            lower_post_start_y)

        # create add higher posts
        text += '\n'+self._post_array(
            self.scn["hub_height"] + height_shift,  # higher post height
            higher_post_start_y)

        """
        if self.settings.apv.add_glass_box:
            t_y = (self.sw_modCorner_y + self.allRows_footprint_y
                   + self.settings.apv.glass_box_to_APV_distance)
            # variable cannot be found because not in default()
            # but in inclined tables apv system settings

            t_x = self.allRows_footprint_x
            text += (f'\n!genbox stock_glass glass_wall {t_x} 0.005 5'
                     f' | xform -t {self.sw_modCorner_x} {t_y} 0')
        """

        return text

    def _post_array(
            self, post_height: float, post_start_y: float) -> str:
        """ creats an array of posts for each row using
        APV_Systsettings.mountingStructureDict """

        s_x = self.mount['post_thickness_x']
        s_y = self.mount['post_thickness_y']
        text = (
            f'!genbox {self.mount["material"]} post {s_x} {s_y} {post_height}'
            f' | xform -t {self.post_start_x} {post_start_y} 0 '
            f'-a {self.mount["n_post_x"]} -t {self.post_distance_x} 0 0 '
            f'-a {self.scn["nRows"]} -t 0 {self.scn["pitch"]} 0 '
        )
        return text

    def get_rad_txt_for_cloning_the_apv_system(self) -> str:
        """Usefull for periodic boundary conditions.
        Returns:
            (str): radiance text
        """

        shift_x_array_start = -self.mount['n_apv_system_clones_in_negative_x'] \
            * self.clone_distance_x

        # total count n of cloned system segments
        # (segment = structure + modules without a gap in x direction)
        n_system_segments_x = self.mount['n_apv_system_clones_in_x'] \
            + 1 + self.mount['n_apv_system_clones_in_negative_x']

        if n_system_segments_x > 1:
            return (f'!xform -t {shift_x_array_start} 0 0 '
                    f'-a {n_system_segments_x} -t {self.clone_distance_x} 0 0 '
                    )
        else:
            return '!xform '

    def get_rad_txt_for_ridgeRoofMods_xform(self) -> str:
        if self.settings.apv.mountingStructureType == \
                'framed_single_axes_ridgeRoofMods':
            y_shift = -self.mod["y"]-self.mod['ygap']
            angle = 180-2*self.scn["tilt"]
            p = self.mount['post_thickness_y']/2
            return f'-i 1 -t 0 {y_shift} 0 -a 2 -rx {angle} -i 1 -t 0 {p} 0'
        else:
            return ''

    def make_checked_module_text(self) -> str:
        """
        Copyright (c) 2017-2021, Alliance for Sustainable Energy, LLC
        All rights reserved. (see BSD 3-Clause License)

        copied from br.main.RadianceObj.makeModule() and modified
        """


        mod = self.mod
        c = self.settings.apv.cellLevelModuleParams

        x = c['numcellsx']*c['xcell']+(c['numcellsx']-1)*c['xcellgap']
        y = c['numcellsy']*c['ycell']+(c['numcellsy']-1)*c['ycellgap']

        if self.settings.apv.glass_modules:
            z = 0.001  # module thickness
        else:
            z = 0.020

        material = 'black'
        # first PV cell
        text = f"! genbox {material} cellPVmodule {c['xcell']} {c['ycell']} {z} | "

        # shift cell to lower corner
        text += 'xform -t {} {} {} '.format(
            -x/2.0,  # + cc,
            (-y*mod['numpanels']/2.0)-(mod['ygap']*(mod['numpanels']-1) / 2.0),
            0  # offset from axis
        )

        # checker board
        text += '-a {} -t {} 0 0 '.format(
            int(c['numcellsx']/2),
            2 * (c['xcell'] + c['xcellgap']))

        text += '-a {} -t 0 {} 0 '.format(
            c['numcellsy']/2,
            2 * (c['ycell'] + c['ycellgap']))

        text += '-a {} -t {} {} 0 '.format(
            2,
            c['xcell'] + c['xcellgap'],
            c['ycell'] + c['ycellgap'])

        # copy module in y direction
        text += '-a {} -t 0 {} 0'.format(mod['numpanels'], y+mod['ygap'])

        return text
