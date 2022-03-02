# #
"""apv main"""


if __name__ == '__main__':
    from pvlib import location
    from pathlib import Path
    import importlib as imp
    import apv
    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.classes.br_wrapper)

    SimSettings = apv.settings.sim_settings.Simulation()
    # APV_SystSettings = apv.settings.apv_systems.Default()
    APV_SystSettings = \
        apv.settings.apv_systems.SimpleSingleCheckerBoard()

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

    brObj = apv.classes.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings
    )
    brObj.setup_br()
    # #
    brObj.view_scene(
        # view_name='module_zoom'
    )
    # #
    brObj.run_raytracing_simulation()

    # plot existing data (simulation cell does not need to be repeated)
    brObj.plot_ground_heatmap()

    # show result data frame
    brObj.df_ground_results

    # #
