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
    sceneDict = simSettings.sceneDict
    moduleDict = simSettings.moduleDict

    y_length = sceneDict['pitch']*(sceneDict['nRows']-1)
    x_length = moduleDict['x'] * (sceneDict['nMods']) + 0.4

    y_start = -y_length / 2
    x_start = -x_length / 2

    if sceneDict['nMods'] % 2 == 0:
        x_start += moduleDict['x']/2

    # create posts
    text = (f'! genbox {material} post 0.15 0.15 {sceneDict["hub_height"]+0.1}'
            f' | xform  -t {x_start} {y_start} 0 \
           -a 2 -t {x_length} 0 0 -a 3 -t 0 {sceneDict["pitch"]} 0 ')
    # create horizontal beams
    text += (f'\n! genbox {material} post 0.1 {y_length} 0.1 \
           | xform  -t {x_start} {y_start} {sceneDict["hub_height"]-0.1} \
           -a 2 -t {x_length} 0 0 -a 2 -t 0 0 {-0.5} ')

    return text


def create_mounting_structure0(simSettings,
                               radObj,
                               scene,
                               oct_file_name,
                               material):
    """Creates Aluminum posts and mounting structure

    Args:
        simSettings : inherited from br_wrapper
        radObj : inherited from br_wrapper
        scene : appends to scene inherited from br_wrapper
        oct_file_name : inherited from br_wrapper

    Returns:
        oct_file: created new oct file including all objects
    """
    sceneDict = simSettings.sceneDict
    moduleDict = simSettings.moduleDict
    num_of_posts = sceneDict['nRows']
    # xstart and y start change with azimuth
    xstart = round(sceneDict['nMods']*moduleDict['x']/2 + 1)
    if sceneDict['nMods'] % 2 == 0:
        # xstart2 for parrallel and adjust symmetry according to # of modules
        xstart2 = -xstart + moduleDict['x']
    else:
        xstart2 = -xstart

    ystart = sceneDict['pitch']*(sceneDict['nRows']-2)
    height = sceneDict['hub_height']
    rotate = 180 - sceneDict['azimuth']
    for post in np.arange(0, num_of_posts*2, 2):
        name_1 = 'Post{}'.format(post)
        name_2 = 'Post{}'.format(post+1)
        # create post
        text1 = '! genbox {} post 0.1 0.2 {} | xform  -t {} {} 0'.format(
            material, height+0.2, xstart, ystart)
        customObject = radObj.makeCustomObject(name_1, text1)
        radObj.appendtoScene(radfile=scene.radfiles,
                             customObject=customObject,
                             text="!xform -rz {}".format(rotate))
        # post in parallel
        text2 = '! genbox {} post 0.1 0.2 {} | xform  -t {} {} 0'.format(
            material, height+0.2, xstart2, ystart)
        customObject = radObj.makeCustomObject(name_2, text2)

        radObj.appendtoScene(radfile=scene.radfiles,
                             customObject=customObject,
                             text="!xform -rz {}".format(rotate))
        # connection between posts
        # text3 = '! genbox {} post {} 0.2 0.1 | xform  -t {} {} {}'.format(
        #     material, abs(xstart2*2+2), xstart2, ystart, height-1)
        # customObject = radObj.makeCustomObject(name_1+'_'+name_2, text3)

        # radObj.appendtoScene(radfile=scene.radfiles,
        #                      customObject=customObject,
        #                      text="!xform -rz {}".format(rotate))

        ystart -= sceneDict['pitch']

    # Add horizontal beams
    name_3 = 'horPost1'
    name_4 = 'horPost2'
    name_5 = 'horPost3'
    name_6 = 'horPost4'
    length = sceneDict['pitch']*(sceneDict['nRows']-1)
    shift = xstart + 0.2
    shift2 = xstart2 - 0.2
    # horizontal-1
    text4 = '! genbox {} post 0.1 {} 0.1 | xform  -t {} {} {}'.format(
            material, length, shift, -sceneDict['pitch'], height-0.5)
    customObject = radObj.makeCustomObject(name_3, text4)
    radObj.appendtoScene(radfile=scene.radfiles,
                         customObject=customObject,
                         text="!xform -rz {}".format(rotate))
    # horizontal-2
    text5 = '! genbox {} post 0.1 {} 0.1 | xform  -t {} {} {}'.format(
            material, length, shift2, -sceneDict['pitch'], height-0.5)
    customObject = radObj.makeCustomObject(name_4, text5)

    radObj.appendtoScene(radfile=scene.radfiles,
                         customObject=customObject,
                         text="!xform -rz {}".format(rotate))
    # horizontal-3 over 1
    text6 = '! genbox {} post 0.1 {} 0.1 | xform  -t {} {} {}'.format(
        material, length, shift, -sceneDict['pitch'], height-1)
    customObject = radObj.makeCustomObject(name_5, text6)
    radObj.appendtoScene(radfile=scene.radfiles,
                         customObject=customObject,
                         text="!xform -rz {}".format(rotate))
    # horizontal-4 over 2
    text7 = '! genbox {} post 0.1 {} 0.1 | xform  -t {} {} {}'.format(
            material, length, shift2, -sceneDict['pitch'], height-0.75)
    customObject = radObj.makeCustomObject(name_6, text7)

    radObj.appendtoScene(radfile=scene.radfiles,
                         customObject=customObject,
                         text="!xform -rz {}".format(rotate))

    octfile = radObj.makeOct(radObj.getfilelist(),
                             octname=oct_file_name)

    return octfile
