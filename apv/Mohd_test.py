# #
from bifacial_radiance import RadianceObj, AnalysisObj
import bifacial_radiance
import os
import bifacial_radiance
import numpy as np
from pathlib import Path
import subprocess

testfolder = (
    r'C:\Users\moham\Documents\bifacial_radiance-main\bifacial_radiance-main\bifacial_radiance\TEMP')

print("Your simulation will be stored in %s" % testfolder)


# #
demo = RadianceObj("E-W", path=testfolder)
demo.setGround(0.62)
epwfile = demo.getEPW(lat=37.5, lon=-77.6)
metdata = demo.readWeatherFile('EPWs\\USA_VA_Richmond.Intl.AP.724010_TMY.epw')
fullYear = True
demo.gendaylit(4020)  # Noon, June 17th  . # Gencumsky could be used too.
module_type = 'Prism Solar Bi60 landscape'
# #

x = 1.7
y = 1
z = 0.01
Ny = 2
ygap = 0.02
offsetfromaxis = 0.01

moduleDict = {
    'x': x,
    'y': y,
    'xgap': 0.002,
    'ygap': 0.05,
    'zgap': 0,
    'numpanels': Ny
}

sceneDict = {'tilt': 30, 'pitch': 5, 'clearance_height': 4.5,
             'azimuth': 90, 'nMods': 5, 'nRows': 2, 'appendRadfile': True,
             'originx': 0, 'originy': 0}


def make_text_EW(name, moduleDict, sceneDict):
    """creates needed text needed in makemodule() to create E-W. Azimuth angle
    must be 90! and number of panels must be 2!

    Args:
        name ([str]): module_type

    Returns:
        text [str]: [text to rotate second panel to create E-W (270 - 90)]
    """

    name2 = str(name).strip().replace(' ', '_')
    text = '! genbox black {} {} {} {} '.format(name2, x, y, z)
    text += '| xform -t {} {} {} '.format(-x/2.0,
                                          (-y*Ny/2.0)-(ygap*(Ny-1)/2.0),
                                          offsetfromaxis)
    rotation_angle = 2*(90 - sceneDict['tilt']) + 180
    text += '-a {} -t 0 {} 0 -rx {}'.format(Ny, y+ygap, rotation_angle)

    packagingfactor = 100.0
    return text


# #
demo.makeModule(name=module_type, **moduleDict, text=make_text_EW2(module_type))

sceneObj1 = demo.makeScene(module_type, sceneDict)

# #
# sceneDict2 = {'tilt': 30, 'pitch': 5, 'clearance_height': 4.5, 'azimuth': 270,
#               'nMods': 5, 'nRows': 2, 'appendRadfile': True,
#               'originx': 0, 'originy': 0}
# module_type2 = 'Longi'
# demo.makeModule(name=module_type2, **moduleDict, text= make_text_EW(module_type))
# sceneObj2 = demo.makeScene(module_type2, sceneDict2)

# #
octfile = demo.makeOct(demo.getfilelist())
# #
view_fp = os.path.join(testfolder, 'views', 'front.vp')
with open(view_fp, 'w') as f:
    f.write('rvu -vtv -vp '              # vp = view port
            + '0 '                     # X (depth)
            + '-7 '                    # Y (left / right)
            + '6 '                       # Z (height)
            + '-vd 0 6 -1 '   # vd = view direction
            + '-vu 0 0 1 '               # vu = view "Up" ???
            + '-vh 110 -vv 45 '          # vh/vv = horizontal/vertical display
            + '-vo 0 -va 0 '             # vo/va: clipping plane before/after
            + '-vs 0 -vl 0')             # vs/vl: horizontal/vertical
subprocess.call(
    ['rvu', '-vf', view_fp, '-e', '.01', 'E-W'+'.oct'])

# #
analysis = AnalysisObj(octfile=octfile, name='E-W')

# #
sensor = 20
front, back = analysis.moduleAnalysis(scene=sceneObj1,
                                      sensorsy=sensor)


# #
results = analysis.analysis(octfile, name='E-W', frontscan=front,
                            backscan=back)

# #
bifacial_radiance.load.read1Result('results\irr_{}.csv'.format(demo.basename))

# #
bifacial_radiance.load.read1Result('results\irr_{}2.csv'.format(demo.basename))

# #
