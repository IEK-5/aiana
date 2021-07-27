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

    text = '! genbox black cellPVmodule {} {} {} | '.format(
        c['xcell'], c['ycell'],
        0.02  # module thickness
    )
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
        2 * (c['xcell'] + c['xcellgap']))

    text += '-a {} -t 0 {} 0 '.format(
        c['numcellsy']/2,
        2 * (c['ycell'] + c['ycellgap']))

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
    x = m['x']
    y = m['y']
    z = 0.02
    Ny = m['numpanels']  # currently must be 2
    ygap = m['ygap']
    offsetfromaxis = 0.01
    rotation_angle = 2*(90 - c['tilt']) + 180

    name2 = str(name).strip().replace(' ', '_')
    text = '! genbox black {} {} {} {} '.format(name2, x, y, z)
    text += '| xform -t {} {} {} '.format(-x/2.0,
                                          (-y*Ny/2.0)-(ygap*(Ny-1)/2.0),
                                          offsetfromaxis)

    text += '-a {} -t 0 {} 0 -rx {}'.format(Ny, y+ygap, rotation_angle)
    packagingfactor = 100.0

    return text
