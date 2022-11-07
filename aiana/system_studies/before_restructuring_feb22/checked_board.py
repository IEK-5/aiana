# #
"""apv main"""


if __name__ == '__main__':
    from pvlib import location
    from pathlib import Path
    import importlib as imp
    import aiana
    imp.reload(aiana.classes.geometries_handler)
    imp.reload(aiana.classes.br_wrapper)

    SimSettings = aiana.settings.sim_settings.Simulation()
    # APV_SystSettings = apv.settings.apv_systems.Default()
    APV_SystSettings = \
        aiana.settings.apv_systems.SimpleSingleCheckerBoard()

    # ### often changed settings:  ####
    # SimSettings.only_ground_scan = False
    # use_multi_processing = False
    # SimSettings.add_mounting_structure = False
    SimSettings.apv_location = location.Location(
        36.7922, -119.7932, altitude=94, tz=-7, name='Fresno_CA')
    SimSettings.sim_date_time = '06-01_11h'  # whole day
    SimSettings.spatial_resolution = 0.01  # 0.01
    SimSettings.sim_name = 'checker_board_Perna2'  # TODO, cell gaps?

    APV_SystSettings.ground_scan_margin_x = 0
    APV_SystSettings.ground_scan_margin_y = 0
    # APV_SystSettings.sceneDict['nRows'] = 3
    # APV_SystSettings.sceneDict['nMods'] = 6

    aiana = aiana.classes.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings
    )
    aiana.setup_br()
    # #
    aiana.view_scene(
        # view_name='module_zoom'
    )
    # #
    aiana.run_raytracing_simulation()

    # plot existing data (simulation cell does not need to be repeated)
    aiana.plot_ground_heatmap()

    # show result data frame
    aiana.df_ground_results

    # #
