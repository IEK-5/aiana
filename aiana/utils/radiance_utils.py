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
from pathlib import Path
from typing import Literal


def makeCustomMaterial(
    rad_mat_file: Path,
    mat_name: str,
    mat_type: Literal['glass', 'metal', 'plastic', 'trans'],
    R: float = 0, G: float = 0, B: float = 0,
    specularity: float = 0, roughness: float = 0,
    transmissivity: float = 0, transmitted_specularity: float = 0,
    debug_mode=False
):
    """radiance materials input documentation:
    https://floyd.lbl.gov/radiance/refer/ray.html#Materials or
    https://www.radiance-online.org/archived/radsite/radiance/refer/Notes/materials.html

    specularity and roughness effect examples:
    https://thinkmoult.com/radiance-specularity-and-roughness-value-examples.html
    """

    # read old file
    with open(rad_mat_file, 'r') as f:
        lines: list = f.readlines()
        f.close()

    # write new file
    with open(rad_mat_file, 'w') as f:
        print_string = 'Creating'
        lines_new = lines
        for i, line in enumerate(lines):
            words = line.split(' ')
            if len(words) == 3 and words[-1][:-2] == mat_name:
                print_string = 'Overwriting'
                # slice away existing material
                lines_new = lines[:i-1] + lines[i+4:]
                break
        # check for extra line break at the current file end,
        # after which custom materials will be added
        if lines_new[-1][-1:] == '\n':
            text = ''
        else:
            text = '\n'
        # number of modifiers needed by Radiance
        mods = {'glass': 3, 'metal': 5, 'plastic': 5, 'trans': 7}

        # create text for Radiance input:
        text += (f'\nvoid {mat_type} {mat_name}\n0\n0'
                 f'\n{mods[mat_type]} {R} {G} {B}')
        if mods[mat_type] > 3:
            text += f' {specularity} {roughness}'
        if mods[mat_type] > 5:
            text += f' {transmissivity} {transmitted_specularity}'
        if debug_mode:
            print(f"{print_string} custom material {mat_name}.")
        f.writelines(lines_new + [text])
        f.close()


def write_viewfile_in_vp_format(
        scene_camera_dict: dict, view_fp: Path,
        view_type: Literal['perspective', 'parallel'] = 'perspective',
        tool='rvu'
):
    """options manual:
        https://www.radiance-online.org/learning/documentation/manual-pages/pdfs/rpict.pdf/view
    """

    scd = scene_camera_dict.copy()

    # key conversion from float to string with trailing space for cmd
    for key in scd:
        if key[-1] != ' ':
            scd[key] = str(scd[key]) + ' '

    if view_type == 'parallel':
        t = 'l'
    else:  # perspective
        t = 'v'

    with open(view_fp, 'w') as f:
        f.write(
            f'{tool} -vt{t} -vp '
            + scd['cam_pos_x']
            + scd['cam_pos_y']
            + scd['cam_pos_z']
            + '-vd '
            + scd['view_direction_x']
            + scd['view_direction_y']
            + scd['view_direction_z']
            + '-vu 0 0 1 '
            + '-vh '
            + scd['horizontal_view_angle']
            + '-vv '
            + scd['vertical_view_angle']
            # + '-vs 0 -vl 0' # ist in der demo von acceleradRT nicht drin
            # braucht man das?
        )
        f.close()
