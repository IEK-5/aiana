# #
if __name__ == '__main__':
    import importlib as imp
    import apv
    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.classes.br_wrapper)

    SimSettings = apv.settings.sim_settings.Simulation()
    APV_SystSettings = \
        apv.settings.apv_systems.Default()
    APV_SystSettings.add_groundScanArea_as_object_to_scene = True
    # ### often changed settings:  ####

    ###############################################
    # 21. Juni
    # rise: 5:20
    # set: 21:52
    SimSettings.sim_date_time = '6-21_15:00'
    ###############################################

    SimSettings.spatial_resolution = 5
    SimSettings.time_step_in_minutes = 60  # 6

    SimSettings.sim_name = 'debug'

    brObj = apv.classes.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        # debug_mode=True
    )
    brObj.setup_br()

# #
if __name__ == '__main__':
    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.classes.br_wrapper)

    for azimuth in [180]:
        # for azimuth in range(180, 361, 30):
        APV_SystSettings.sceneDict['azimuth'] = azimuth
        APV_SystSettings.scene_camera_dicts[
            'top_down']['horizontal_view_angle'] = 45
        APV_SystSettings.scene_camera_dicts[
            'top_down']['vertical_view_angle'] = 45

        APV_SystSettings.add_airrails = False
        # APV_SystSettings.module_form = 'none'
        x_reduction = -((APV_SystSettings.moduleDict['x']
                         + APV_SystSettings.moduleDict['xgap'])
                        * (APV_SystSettings.sceneDict['nMods']))/2+2  # =2*2m=4m
        y_reduction = (-APV_SystSettings.sceneDict['pitch']
                       - APV_SystSettings.moduleDict['y']/2)
        APV_SystSettings.ground_scan_margin_x = x_reduction  # -3
        APV_SystSettings.ground_scan_margin_y = y_reduction  # -32
        APV_SystSettings.ground_scan_shift_x = 2  # -32
        APV_SystSettings.ground_scan_shift_y = 0
        APV_SystSettings.n_apv_system_clones_in_x = 1

        brObj.create_oct_file(
            APV_SystSettings=APV_SystSettings
        )

        brObj.view_scene(
            view_name='top_down', view_type='parallel'
        )
    # #
    brObj.view_scene(
        view_name='top_down', view_type='parallel'
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


# #
