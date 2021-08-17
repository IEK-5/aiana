import numpy as np
from apv import settings
from apv.settings import Simulation as simSettingsObj


def checked_module(simSettings: simSettingsObj) -> str:
    c = simSettings.cellLevelModuleParams
    m = simSettings.moduleDict

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


def make_text_EW(simSettings: simSettingsObj) -> str:
    """creates needed text needed in makemodule() to create E-W. Azimuth angle
    must be 90! and number of panels must be 2!

    Args:
        simSettings:
        name ([str]): module_type
        moduleDict ([dict]): inherited from br_setup and defined in settings.py
        sceneDict  ([dict]): inherited from br_setup and defined in settings.py

    Returns:
        text [str]: [text to rotate second panel to create E-W (270 - 90)]
    """
    c = simSettings.sceneDict
    m = simSettings.moduleDict
    name = settings.Simulation.sim_name

    z = 0.02
    Ny = m['numpanels']  # currently must be 2
    offsetfromaxis = 0.01
    rotation_angle = 2*(90 - c['tilt']) + 180

    name2 = str(name).strip().replace(' ', '_')
    text = '! genbox {} {} {} {} {} '.format(name2, m['x'], m['y'], z)
    text += '| xform -t {} {} {} '.format(
        -m['x']/2.0,
        (-m['y']*Ny/2.0)-(m['ygap']*(Ny-1)/2.0),
        offsetfromaxis
    )

    text += '-a {} -t 0 {} 0 -rx {}'.format(
        Ny, m['y']+m['ygap'], rotation_angle)
    packagingfactor = 100.0

    return text


def cell_level_EW_fixed(simSettings: simSettingsObj,
                        cellLevelModuleParams) -> str:
    """creates needed text needed in makemodule() to create cell-level E-W.
    Azimuth angle must be 90! and number of panels must be 2!

    Args:
        simSettings:
        name ([str]): module_type
        moduleDict ([dict]): inherited from br_setup and defined in settings.py
        sceneDict  ([dict]): inherited from br_setup and defined in settings.py

    Returns:
        text [str]: [text to rotate second panel to create E-W (270 - 90)]
    """
    sc = simSettings.sceneDict
    m = simSettings.moduleDict
    name = settings.Simulation.sim_name
    z = 0.02
    Ny = m['numpanels']  # currently must be 2
    offsetfromaxis = 0.01
    rotation_angle = 2*(90 - sc['tilt']) + 180

    name2 = str(name).strip().replace(' ', '_')
    c = cellLevelModuleParams
    x = c['numcellsx']*c['xcell'] + (c['numcellsx']-1)*c['xcellgap']
    y = c['numcellsy']*c['ycell'] + (c['numcellsy']-1)*c['ycellgap']

    # center cell -
    if c['numcellsx'] % 2 == 0:
        cc = c['xcell']/2.0
        print("Module was shifted by {} in X to\
              avoid sensors on air".format(cc))

    text = '! genbox {} cellPVmodule {} {} {} | '.format(c['xcell'],
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


def mounting_structure(simSettings, material):
    """Creates Aluminum posts and mounting structure

    Args:
        simSettings : inherited from br_wrapper
        scene : appends to scene inherited from br_wrapper

    Returns:
        oct_file: created new oct file including all objects
    """
    sDict = simSettings.sceneDict
    mDict = simSettings.moduleDict

    s_beam = 0.075  # beam thickness
    d_beam = 0.5  # beam distance
    s_post = 0.15  # post thickness
    h_post = sDict["hub_height"] + 0.2  # post height
    y_length = sDict['pitch']*(sDict['nRows'] - 1)
    x_length = mDict['x'] * (sDict['nMods'] + 1)

    y_start = -y_length / 2
    x_start = -x_length / 2

    if sDict['nMods'] % 2 == 0:
        x_start += mDict['x']/2

    # create posts
    text = (f'! genbox {material} post {s_post} {s_post} {h_post}'
            f' | xform  -t {x_start} {y_start} 0 \
           -a 2 -t {x_length} 0 0 -a 3 -t 0 {sDict["pitch"]} 0 ')
    # create horizontal beams in y direction
    text += (f'\n! genbox {material} post {s_beam} {y_length} {s_beam} \
           | xform  -t {x_start} {y_start} {h_post - s_beam - 0.4} \
           -a 2 -t {x_length} 0 0 -a 2 -t 0 0 {-d_beam} ')
    # create horizontal beams in x direction
    text += (f'\n! genbox {material} post {x_length} {s_beam} {s_beam} \
            | xform  -t {x_start} {y_start} {h_post - s_beam - 0.2} \
            -a 3 -t 0 {sDict["pitch"]} 0 -a 2 -t 0 0 {-d_beam} ')
    return text
