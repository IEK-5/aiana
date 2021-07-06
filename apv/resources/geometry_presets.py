"""later more presets can be added here

from bifacial_radiance package tutorials:

### moduleDict:
x: module width
y: module height (commonly y is > x and the module is fixed along x)
xgap: Distance between modules in the row
ygap: Distance between the 2 modules along the collector slope.
zgap: If there is a torquetube, this is the distance between the
      torquetube and the modules. If there is not a module, zgap
      is the distance between the module and the axis of rotation
      (relevant for tracking systems).
numpanels: number of panels along y

### sceneDict:
tilt: panel tilt [degree]
pitch: distance between two adjacent rows [m]
hub_height: vert. distance: ground to modules [m]
azimuth: panel face direction [degree]
nMods: modules per row (along x in moduleDict) [-]
nRows: number of rows [-]

"""


class APV_Morschenich:

    moduleDict = {
        'x': 0.998,
        'y': 1.980,
        'xgap': 0.002,
        'ygap': 0.05,
        'zgap': 0,
        'numpanels': 2
    }

    sceneDict = {
        'tilt': 20,
        'pitch': 10,
        'hub_height': 4.5,
        'azimuth': 180,
        'nMods': 10,
        'nRows': 3
    }
