
import numpy as np
from aiana.classes.rad_txt_related.geometry_basics import GeomBasics
from aiana.classes.util_classes.settings_handler import Settings


class Morschenich(GeomBasics):

    l_x: float  # complete apv distance first to last post in x
    # (equal edge to edge, not both post's outer edge)
    l_y: float  # complete apv distance first to last post in y

    """uses coordinates such as apv system south west corner and
    methods such as inclined_tables from the GeomBasics class by
    inherence"""

    def __init__(self, settings: Settings):
        super().__init__(settings)
        # overwrite / create for Morschenich special case:
        # mounting_lengths_x "l_x":
        self.l_x = 40  # from drawings (20*2m)
        self.sp_x = self.mount['post_thickness_x']
        self.l_y = self.scn["pitch"]*(self.scn["nRows"]-1)\
            + self.mount['inner_table_post_distance_y']
        self.post_start_x = (-self.l_x+self.sp_x)/2+self.center_offset_x

    def morschenich_fixed(self) -> str:
        """
        starts with inclined tables, which creates all posts
        except the middle posts at the side. Later other structur elements
        are added with helper methods (starting with an underscore).
        """

        text = self.inclined_tables()

        # add rails and outer frame
        hh = 2.5
        middle_post_start_y = self.modFootPrint_start_y+self.singleRow_footprint_y/2

        post_dist_y = self.mount['inner_table_post_distance_y']/2
        # (/2 as there are 3 instead of 2 post at the outer frame)
        text += self._rails_between_modules(middle_post_start_y+post_dist_y, hh)\
            + self._outer_frame(middle_post_start_y-post_dist_y, hh)

        if self.settings.apv.add_trans_plastic_between_modules:
            text += self._corrugated_glass_between_modules(middle_post_start_y+post_dist_y)

        # add straight thicker rail ("Regenrinne"!):
        sb_x = self.module_footprint_length_x
        sb_y = 0.16  # TODO how much?
        sb_z = 0.08
        z_start = self.scn["hub_height"] \
            - (self.mount['inner_table_post_distance_y']+sb_y)\
            * np.tan(self.scn['tilt']*np.pi/180) - sb_z
        y_start2 = middle_post_start_y-post_dist_y-sb_y+self.scn['pitch']

        text += (
            f'\n!genbox {self.mount["material"]} post {sb_x} {sb_y} {sb_z}'
            f' | xform -t {self.modFootPrint_start_x} {y_start2} {z_start} '
            + self._row_array(nRowsReduc=1)
        )

        return text

    def _row_array(self, nRowsReduc=0) -> str:
        return f'-a {self.scn["nRows"]-nRowsReduc} -t 0 {self.scn["pitch"]} 0 '

    def _clone_to_other_side_in_x(self, x_shift=0) -> str:
        return f'-a 2 -t {self.l_x+x_shift} 0 0 '

    def _outer_frame(self, y_start, hh) -> str:

        sp_x = self.mount['post_thickness_x']
        sp_y = self.mount['post_thickness_y']
        # middle post
        middle_post_start_y = self.modFootPrint_start_y+self.singleRow_footprint_y/2
        post_height = self.scn["hub_height"]

        text = (
            f'\n!genbox {self.mount["material"]} post {sp_x} {sp_y} {post_height}'
            f' | xform -t {self.post_start_x} {middle_post_start_y} 0 '
            + self._row_array()
            + self._clone_to_other_side_in_x()
        )

        # ### outer beams ###
        height_array = f'-a 3 -t 0 0 -1.12 '
        # short side (parallel to y) below modules
        sb_x = 0.06
        sb_y = self.mount['inner_table_post_distance_y']+sp_y
        sb_z = 0.04
        text += (
            f'\n!genbox {self.mount["material"]} post {sb_x} {sb_y} {sb_z}'
            f' | xform -t {self.post_start_x-sb_x} {y_start} {hh-sb_z} '
            + height_array
            + self._row_array()
            + self._clone_to_other_side_in_x(sb_x+sp_x)
        )

        sb_x = self.l_x+sp_x
        sb_y = 0.06
        # long side (parallel to x)
        text += (
            f'\n!genbox {self.mount["material"]} post {sb_x} {sb_y} {sb_z}'
            f' | xform -t {self.post_start_x} {y_start-sb_y} {hh-sb_z} '
            # + height_array  #only for south facility with plexi glass
            f'-a 2 -t 0 {self.l_y+sp_y+sb_y} 0 '  # clone to other side in y direct.
        )

        return text

    def _corrugated_glass_between_modules(self, y_start: float,
                                          tilt=-14, height=3.8) -> str:
        """TODO still quick and dirty... move out morschenich to extra file?
        y_start = y_start of the upper edge
        (upper for the default negative tilt)
        height = where the upper edge of the inclined cover starts
        """
        sp_y = self.mount['post_thickness_y']
        return (
            f'\n!genbox glass cover {self.l_x} {4.71} {0.01} '
            f'| xform -rx {tilt} -t {self.post_start_x} '
            f'{y_start+self.scn["pitch"]} {height+sp_y+0.06} '
            + self._row_array(nRowsReduc=2)
        )

    def _rails_between_modules(
        self, y_start: float, hh: float, tilt=-14, height=3.8, n_rails=8,
    ) -> str:
        """y_start = y_start of the (upper) height anchor of the rails
        (upper for the default negative tilt)
        hh = height_horizontal bar as in drawing 2.5m
        height = where the inclined rails start (upper)
        """

        sp_x = self.mount['post_thickness_x']
        sp_y = self.mount['post_thickness_y']

        def _horizontal_beams_below_rails(sb_x, sb_z, z_shift):
            "sb = thickness bar, sp = thickness post"
            return (
                f'\n!genbox {self.mount["material"]} post {sb_x} {4.5+2*sp_y} {sb_z}'
                f' | xform -t {self.post_start_x-sb_x} {y_start} {hh+z_shift} '
                + self._row_array(nRowsReduc=1)
                + self._clone_to_other_side_in_x(sb_x+sp_x)
            )
        # lower (touching)
        text = _horizontal_beams_below_rails(0.04, 0.12, 0)
        # upper
        text += _horizontal_beams_below_rails(0.06, 0.04, 0.12)

        # inclined thicker beams in parallel to y
        text += (
            f'\n!genbox {self.mount["material"]} post {sp_x} {4.71} {sp_y}'
            f' | xform -rx {tilt} -t {self.post_start_x} {y_start} {height} '
            f'-a {self.mount["n_post_x"]*2-1} -t 2 0 0 '
            + self._row_array(nRowsReduc=1)
        )
        # straight thinner rails in steps parallel to x
        sb_x = self.l_x+sp_x
        sb_y = 0.041
        sb_z = 0.06
        clone_dist = 0.6
        y_clone_dist = clone_dist*np.cos(tilt*np.pi/180)
        height += sp_y*(1+np.tan(tilt*np.pi/180))  # to lay on top of beams
        z_clone_dist = y_clone_dist*np.tan(tilt*np.pi/180)

        text += (
            f'\n!genbox {self.mount["material"]} post {sb_x} {sb_y} {sb_z}'
            f' | xform -rx {tilt} -t {self.post_start_x} {y_start+sp_y} {height} '

            f'-a {n_rails} -t 0 {y_clone_dist} {z_clone_dist} '
            + self._row_array(nRowsReduc=1)
        )

        # diagonals below rails
        alpha = np.arctan(0.6*7/4)*180/np.pi
        length = ((0.6*7)**2+4**2)**0.5  # 5.8
        for rz in [-alpha, alpha]:
            if rz == -alpha:
                y_shift = np.sin(alpha*np.pi/180)*length
            else:
                y_shift = 0
            text += (
                f'\n!genbox {self.mount["material"]} post {length} 0.07 0.01'
                f' | xform -rz {rz} -t {sb_y/2} {y_shift} 0'
                f' -rx {tilt} -t {self.post_start_x} {y_start+sp_y} {height} '
                + self._row_array(nRowsReduc=1)
                + self._clone_to_other_side_in_x(-4)
            )

        return text
