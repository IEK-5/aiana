# #
"""apv main"""

if __name__ == '__main__':
    from pathlib import Path
    import importlib as imp
    import apv
    imp.reload(apv.utils.GeometriesHandler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.br_wrapper)

    SimSettings = apv.settings.simulation.Simulation()
    APV_SystSettings =\
        apv.settings.apv_systems.APV_Syst_InclinedTables_Juelich()
    # APV_SystSettings = apv.settings.apv_systems.SimpleForCheckerBoard()
    APV_SystSettings = apv.settings.apv_systems.Default()

    # ### often changed settings:  ####
    # SimSettings.only_ground_scan = False
    # use_multi_processing = False
    # SimSettings.add_mounting_structure = False
    SimSettings.sim_date_time = '07-15_18h'
    SimSettings.spatial_resolution = 0.1
    # SimSettings.sky_gen_mode = 'gencumsky'
    # SimSettings.sim_name = 'declined_tables_and_glassbox'
    APV_SystSettings.moduleDict['xgap'] = 0.05
    # APV_SystSettings.mounting_structure_type = 'declined_tables'
    # APV_SystSettings.sceneDict['nRows'] = 3

    # APV_SystSettings.sceneDict['nMods'] = 4
    # APV_SystSettings.sceneDict['nRows'] = 4
    # APV_SystSettings.sceneDict['pitch'] = 4
    # APV_SystSettings.sceneDict['azimuth'] = 200
    # APV_SystSettings.moduleDict['y'] = 0.5
    # APV_SystSettings.mounting_structure_type = 'none'
    # APV_SystSettings.module_form = 'none'
    # APV_SystSettings.glass_modules = True
    APV_SystSettings.round_up_field_dimensions = False
    APV_SystSettings.scene_camera_dicts[
        'top_down']['horizontal_view_angle'] = 55
    APV_SystSettings.scene_camera_dicts[
        'top_down']['vertical_view_angle'] = 50

    APV_SystSettings.ground_scan_margin_x = 3  # -3
    APV_SystSettings.ground_scan_margin_y = 8  # -32
    APV_SystSettings.ground_scan_shift_x = 2  # -32
    APV_SystSettings.ground_scan_shift_y = 4  # -32

    weather_file = apv.settings.user_pathes.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    brObj = apv.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        weather_file=weather_file,  # downloading automatically without this,
        # debug_mode=True
    )
    brObj.setup_br()

    # #
    imp.reload(apv.utils.GeometriesHandler)
    imp.reload(apv.br_wrapper)

    for azimuth in [225]:
        # for azimuth in range(180, 361, 30):

        APV_SystSettings.sceneDict['azimuth'] = azimuth
        brObj._create_geometries(
            APV_SystSettings=APV_SystSettings
        )
        brObj.view_scene(
            view_name='top_down',
            view_type='parallel'
        )
    # #
    brObj.view_scene(
        # view_name='top_down',
        # view_type='parallel'
    )
    # #
if __name__ == '__main__':
    brObj.run_raytracing_simulation()
    # #
    # plot existing data (simulation cell does not need to be repeated)
    brObj.plot_ground_insolation()
    # #
    # show result data frame
    brObj.df_ground_results
