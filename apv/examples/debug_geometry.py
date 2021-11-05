# #
"""apv main"""

from apv.settings import apv_systems


if __name__ == '__main__':
    from pathlib import Path
    import importlib as imp
    import apv
    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.br_wrapper)

    SimSettings = apv.settings.simulation.Simulation()
    SimSettings.use_multi_processing = True
    # APV_SystSettings =\
    #     apv.settings.apv_systems.APV_Syst_InclinedTables_Juelich()
    # APV_SystSettings = apv.settings.apv_systems.SimpleForCheckerBoard()
    APV_SystSettings = apv.settings.apv_systems.Default()
    APV_SystSettings.add_groundScanArea_as_object_to_scene = True
    SimSettings.scan_target = 'ground'
    SimSettings.ray_tracing_accuracy = 'low'
    # ### often changed settings:  ####
    # SimSettings.only_ground_scan = False
    # use_multi_processing = False
    # SimSettings.add_mounting_structure = False

    ###############################################
    # 21. Juni
    # rise: 5:20
    # set: 21:52
    SimSettings.sky_gen_mode = 'gendaylit'
    ###############################################

    SimSettings.spatial_resolution = 5
    SimSettings.irradiance_data_source = 'ADS_satellite'
    print(SimSettings.irradiance_data_source)
    # Insert start end-date of the year as [month,day,hour]
    # SimSettings.sky_gen_mode = 'gencumsky'
    # SimSettings.startdt = '1-1_0h'
    # SimSettings.enddt = '1-31_23h'
    SimSettings.sim_name = 'debug'
    APV_SystSettings.moduleDict['xgap'] = 0.05
    # APV_SystSettings.mounting_structure_type = 'declined_tables'
    # APV_SystSettings.sceneDict['nRows'] = 3

    # APV_SystSettings.sceneDict['nMods'] = 4
    # APV_SystSettings.sceneDict['nRows'] = 4
    # APV_SystSettings.sceneDict['pitch'] = 4
    # APV_SystSettings.sceneDict['azimuth'] = 200
    # APV_SystSettings.moduleDict['y'] = 0.5
    # APV_SystSettings.mounting_structure_type = 'none'
    APV_SystSettings.module_form = 'std'
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

    y_reduction = (-APV_SystSettings.sceneDict['pitch']/2
                   - APV_SystSettings.moduleDict['y'])
    APV_SystSettings.ground_scan_margin_x = 0  # -3
    APV_SystSettings.ground_scan_margin_y = y_reduction  # -32
    APV_SystSettings.ground_scan_shift_x = 0  # -32
    APV_SystSettings.ground_scan_shift_y = 0  # -32

    weather_file = apv.settings.user_paths.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    brObj = apv.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        # weather_file=weather_file,  # downloading automatically without this,
        debug_mode=False
    )

    evalObj = apv.classes.APV_evaluation.APV_Evaluation(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings
    )

    SimSettings.sim_date_time = '6-21_15h'
    brObj.setup_br()
    # evalObj.evaluate_APV(SimSettings=SimSettings)
    # #
    brObj.view_scene(
        view_name='top_down',
        view_type='parallel'
    )
    # #
    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.br_wrapper)

    for azimuth in [225]:
        # for azimuth in range(180, 361, 30):

        APV_SystSettings.sceneDict['azimuth'] = azimuth
        brObj.create_geometries(
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
    brObj.plot_ground_heatmap(cm_unit='PAR')
    # #
    # show result data frame
    brObj.df_ground_results
    # #
    evalObj.evaluate_APV()


# #
