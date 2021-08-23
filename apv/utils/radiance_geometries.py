"""documentation links

    GENBOX (create a box with a certain size)
    https://floyd.lbl.gov/radiance/man_html/genbox.1.html

    GENREV (to create tubes, rings, donats, etc.)
    https://floyd.lbl.gov/radiance/man_html/genrev.1.html

    XFORM (translate, rotate, make arrays):
    https://floyd.lbl.gov/radiance/man_html/xform.1.html

    """

import numpy as np
from apv.settings.apv_systems import Default as APV_SystSettingsObj


def checked_module(APV_SystSettings: APV_SystSettingsObj) -> str:
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


def make_text_EW(APV_SystSettings: APV_SystSettingsObj) -> str:
    """creates needed text needed in makemodule() to create E-W. Azimuth angle
    must be 90! and number of panels must be 2!

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

    z = 0.02
    Ny = mDict['numpanels']  # currently must be 2
    offsetfromaxis = 0.01
    rotation_angle = 2*(90 - sDict['tilt']) + 180

    text = '! genbox {} {} {} {} {} '.format(
        'EW_module', 'black', mDict['x'], mDict['y'], z)
    text += '| xform -t {} {} {} '.format(
        -mDict['x']/2.0,
        (-mDict['y']*Ny/2.0)-(mDict['ygap']*(Ny-1)/2.0),
        offsetfromaxis
    )

    text += '-a {} -t 0 {} 0 -rx {}'.format(
        Ny, mDict['y']+mDict['ygap'], rotation_angle)
    packagingfactor = 100.0

    return text


def cell_level_EW_fixed(APV_SystSettings: APV_SystSettingsObj,
                        cellLevelModuleParams) -> str:
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

    c = cellLevelModuleParams
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


def declined_tables_mount(
        APV_SystSettings: APV_SystSettingsObj) -> str:
    """
    origin x: x-center of the "int(nMods/2)"ths module
    origin y: nRow uneven: y-center of the center row
              nRow even: y_center of the the row south to the system center
    """

    material = 'Metal_Aluminum_Anodized'
    sDict = APV_SystSettings.sceneDict
    mDict = APV_SystSettings.moduleDict

    table_length_x = (mDict['x']+mDict['xgap']) * sDict['nMods']
    table_length_y = (mDict['y']+mDict['ygap']) * mDict['numpanels']

    table_footprint_y = table_length_y*np.cos(sDict['tilt']*np.pi/180)

    # define these: ####
    inner_table_post_distance_y = 3.4  # *table_footprint_y/4.8296
    # table_footprint_y/4.8296 = ca. 1 for given setup
    post_every_nMods = int(sDict['nMods']/2)  # in x (east -> west for azi=180)
    # #########

    post_distance_x = post_every_nMods * (mDict['x']+mDict['xgap'])
    # (post_distance_y = sDict['pitch'])

    posts_start_x = -table_length_x / 2
    if sDict['nMods'] % 2 == 0:
        posts_start_x += (mDict['x']+mDict['xgap'])/2

    # the origin is always in the y-center of a module row
    # and a module row has a y lengths equal to table_footprint_y
    # nRows = 1: first_table_edge_start_y = -table_footprint_y/2
    # nRows = 2: first_table_edge_start_y = -table_footprint_y/2
    # nRows = 3: first_table_edge_start_y = -sDict['pitch']-table_footprint_y/2
    # nRows = 4: first_table_edge_start_y = -sDict['pitch']-table_footprint_y/2
    # nRows = 5: first_table_edge_start_y=-2*sDict['pitch']-table_footprint_y/2
    # nRows = 6: first_table_edge_start_y=-2*sDict['pitch']-table_footprint_y/2
    # ...

    first_table_edge_start_y = (
        - int((sDict['nRows']-1)/2)*sDict['pitch']  # = 0 for nRows = 2
        - table_footprint_y/2
    )

    lower_post_start_y = first_table_edge_start_y + (
        table_footprint_y - inner_table_post_distance_y)/2

    higher_post_start_y = lower_post_start_y + inner_table_post_distance_y

    s_post = 0.15  # post thickness
    height_shift = inner_table_post_distance_y*np.sin(
        sDict['tilt']*np.pi/180)/2
    h_lower_post = sDict["hub_height"] - height_shift  # lower post height
    h_higher_post = sDict["hub_height"] + height_shift  # higher post height

    post_count_in_x = int(round(sDict['nMods']/post_every_nMods)) + 1

    # create lower posts
    text = (f'! genbox {material} post {s_post} {s_post} {h_lower_post}'
            f' | xform -t {posts_start_x} {lower_post_start_y} 0 \
            -a {post_count_in_x} -t {post_distance_x} 0 0 \
            -a {sDict["nRows"]} -t 0 {sDict["pitch"]} 0 ')

    # create lower posts
    text += (f'\n! genbox {material} post {s_post} {s_post} {h_higher_post}'
             f' | xform -t {posts_start_x} {higher_post_start_y} 0 \
            -a {post_count_in_x} -t {post_distance_x} 0 0 \
            -a {sDict["nRows"]} -t 0 {sDict["pitch"]} 0 ')

    # mark origin
    # text += f'\n! genbox {material} post {s_post} {s_post} 20'

    return text


def framed_single_axes_mount(
        APV_SystSettings: APV_SystSettingsObj) -> str:
    """Creates Aluminum posts and mounting structure

    Args:
        APV_SystSettings : inherited from br_wrapper
        scene : appends to scene inherited from br_wrapper

    Returns:
        oct_file: created new oct file including all objects
    """

    material = 'Metal_Aluminum_Anodized'
    sDict = APV_SystSettings.sceneDict
    mDict = APV_SystSettings.moduleDict

    s_beam = 0.075  # beam thickness
    d_beam = 0.5  # beam distance
    s_post = 0.15  # post thickness
    h_post = sDict["hub_height"] + 0.2  # post height
    y_length = sDict['pitch']*(sDict['nRows'] - 1)
    x_length = (mDict['x']+mDict['xgap']) * (sDict['nMods'] + 1)

    y_start = -y_length / 2
    x_start = -x_length / 2

    if sDict['nMods'] % 2 == 0:
        x_start += (mDict['x']+mDict['xgap'])/2

    # create posts
    text = (f'! genbox {material} post {s_post} {s_post} {h_post}'
            f' | xform  -t {x_start} {y_start} 0 \
           -a 2 -t {x_length} 0 0 -a {sDict["nRows"]} -t 0 {sDict["pitch"]} 0 '
            )
    # create horizontal beams in y direction
    text += (f'\n! genbox {material} post {s_beam} {y_length} {s_beam} \
           | xform  -t {x_start} {y_start} {h_post - s_beam - 0.4} \
           -a 2 -t {x_length} 0 0 -a 2 -t 0 0 {-d_beam} ')
    # create horizontal beams in x direction
    text += (f'\n! genbox {material} post {x_length} {s_beam} {s_beam} \
            | xform  -t {x_start} {y_start} {h_post - s_beam - 0.2} \
            -a {sDict["nRows"]} -t 0 {sDict["pitch"]} 0 -a 2 -t 0 0 {-d_beam} '
             )
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
