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
    """type trans = translucent plastic
    radiance materials documentation:
    https://floyd.lbl.gov/radiance/refer/ray.html#Materials"""

    # read old file
    with open(rad_mat_file, 'r') as f:
        lines: list = f.readlines()
        f.close()

    # write new file
    with open(rad_mat_file, 'w') as f:
        print_string = 'Creating'
        lines_new = lines
        for i, line in enumerate(lines):
            if mat_name in line:
                print_string = 'Overwriting'
                # slice away existing material
                lines_new = lines[:i-1] + lines[i+4:]
                break
        # check for extra new line at the end
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

    scd = scene_camera_dict

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
            + '-vs 0 -vl 0'
        )
