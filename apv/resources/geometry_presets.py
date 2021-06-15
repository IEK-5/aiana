"""later more presets can be added here
    """


class APV_Morschenich:
    # units in [m] for distances and in [degree] for angles (tilt, azimuth)

    # bifacial_radiance scene dictionary needed for RadianceObj.makeScene():

    sceneDict = {
        'tilt': 20,
        'pitch': 10,        # distance between two adjacent rows
        'hub_height': 4.5,  # vert. distance: ground to modules
        'azimuth': 180,
        'nMods': 10,        # modules per row
        'nRows': 3
    }
