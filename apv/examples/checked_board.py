# #
"""apv main"""


if __name__ == '__main__':
    from pvlib import location
    from pathlib import Path
    import importlib as imp
    import apv
    imp.reload(apv.utils.radiance_geometries)
    imp.reload(apv.br_wrapper)

    SimSettings = apv.settings.simulation.Simulation()
    # APV_SystSettings = apv.settings.apv_systems.Default()
    APV_SystSettings = \
        apv.settings.apv_systems.SimpleForCheckerBoard()

    # ### often changed settings:  ####
    # SimSettings.only_ground_scan = False
    # use_multi_processing = False
    # SimSettings.add_mounting_structure = False
    SimSettings.apv_location = location.Location(
        36.7922, -119.7932, altitude=94, tz=-7, name='Fresno_CA')
    SimSettings.sim_date_time = '06-01_11h'  # whole day
    SimSettings.spatial_resolution = 0.01  # 0.01
    #SimSettings.sky_gen_mode = 'gencumsky'
    SimSettings.sim_name = 'checker_board_Perna'

    APV_SystSettings.ground_scan_margin_x = 0
    APV_SystSettings.ground_scan_margin_y = 0
    # APV_SystSettings.sceneDict['nRows'] = 3
    # APV_SystSettings.sceneDict['nMods'] = 6

    weather_file = apv.settings.user_pathes.bifacial_radiance_files_folder / \
        Path('EPWs/USA_CA_Fresno.Air.Terminal.723890_TMY3.epw')

    brObj = apv.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        weather_file=weather_file  # downloading automatically without this
    )
    brObj.setup_br()
    # #
    brObj.view_scene(
        # view_name='module_zoom'
    )
    # #
    brObj.run_raytracing_simulation()
    # #

    # plot existing data (simulation cell does not need to be repeated)
    brObj.plot_ground_insolation()

    # show result data frame
    brObj.df_ground_results

    # #
