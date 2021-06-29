"""later more presets can be added here

from bifacial_radiance package tutorials:

moduleDict:
xgap: Distance between modules in the row
ygap: Distance between the 2 modules along the collector slope.
zgap: If there is a torquetube, this is the distance between the
      torquetube and the modules. If there is not a module, zgap
      is the distance between the module and the axis of rotation
      (relevant for tracking systems).

    """


class APV_Morschenich:
    # units in [m] for distances and in [degree] for angles (tilt, azimuth)

    # bifacial_radiance scene dictionary needed for RadianceObj.makeScene():
    moduleDict = {'x': 0.998,
                  'y': 1.980,
                  'xgap': 0.002,
                  'ygap': 0.05,
                  'zgap': 0,
                  'numpanels': 2
                  }

    sceneDict = {
        'tilt': 20,         # panel tilt
        'pitch': 10,        # distance between two adjacent rows
        'hub_height': 4.5,  # vert. distance: ground to modules
        'azimuth': 180,     # panel face direction
        'nMods': 10,        # modules per row
        'nRows': 3          # number of rows
    }
