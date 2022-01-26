# #
if __name__ == '__main__':
    import importlib as imp
    import apv
    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.br_wrapper)

    SimSettings = apv.settings.simulation.Simulation()
    APV_SystSettings = \
        apv.settings.apv_systems.APV_Syst_InclinedTables_S_Morschenich()
    APV_SystSettings.add_groundScanArea_as_object_to_scene = True
    # ### often changed settings:  ####

    ###############################################
    # 21. Juni
    # rise: 5:20
    # set: 21:52
    SimSettings.sim_date_time = '6-21_06:30'
    ###############################################

    SimSettings.spatial_resolution = 5
    SimSettings.time_step_in_minutes = 10  # 6
    # TODO csv file for e.g. 60 needs to be deleted to avoid key error

    SimSettings.sim_name = 'debug'

    brObj = apv.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        # debug_mode=True
    )
    brObj.setup_br()

# #
if __name__ == '__main__':
    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.br_wrapper)

    for azimuth in [180]:
        # for azimuth in range(180, 361, 30):
        APV_SystSettings.sceneDict['azimuth'] = azimuth

        APV_SystSettings.scene_camera_dicts[
            'top_down']['horizontal_view_angle'] = 45
        APV_SystSettings.scene_camera_dicts[
            'top_down']['vertical_view_angle'] = 45

        APV_SystSettings.add_airrails = False
        APV_SystSettings.module_form = 'none'
        x_reduction = -((APV_SystSettings.moduleDict['x']
                         + APV_SystSettings.moduleDict['xgap'])
                        * (APV_SystSettings.sceneDict['nMods']))/2+2  # =2*2m=4m
        y_reduction = (-APV_SystSettings.sceneDict['pitch']
                       - APV_SystSettings.moduleDict['y']/2)
        APV_SystSettings.ground_scan_margin_x = x_reduction  # -3
        APV_SystSettings.ground_scan_margin_y = y_reduction  # -32
        APV_SystSettings.ground_scan_shift_x = 2  # -32
        APV_SystSettings.ground_scan_shift_y = \
            APV_SystSettings.mountingStructureDict[
                'inner_table_post_distance_y']
        brObj.geomObj.x_field = 4
        brObj.create_geometries(
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
    evalObj.evaluate_APV()


# #
