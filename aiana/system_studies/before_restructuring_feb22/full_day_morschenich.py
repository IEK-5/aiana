# #
"""apv main"""

if __name__ == '__main__':
    from pathlib import Path
    import importlib as imp
    import aiana
    imp.reload(aiana.classes.geometries_handler)
    imp.reload(aiana.settings.apv_systems)
    imp.reload(aiana.classes.br_wrapper)

    SimSettings = aiana.settings.sim_settings.Simulation()
    APV_SystSettings = aiana.settings.apv_systems.Default()
    evalObj = aiana.classes.APV_evaluation.APV_Evaluation(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings
    )
    # ### often changed settings:  ####
    SimSettings.spatial_resolution = 1
    print(SimSettings.irradiance_data_source)
    # Insert start end-date of the year as [month,day,hour]
    SimSettings.sky_gen_mode = 'gendaylit'
    APV_SystSettings.moduleDict['xgap'] = 0.02
    # APV_SystSettings.sceneDict['nRows'] = 3

    # APV_SystSettings.sceneDict['nMods'] = 4
    # APV_SystSettings.sceneDict['nRows'] = 4
    # APV_SystSettings.sceneDict['pitch'] = 4
    # APV_SystSettings.sceneDict['azimuth'] = 200
    # APV_SystSettings.moduleDict['y'] = 0.5
    # APV_SystSettings.mounting_structure_type = 'none'
    # APV_SystSettings.module_form = 'none'
    # APV_SystSettings.glass_modules = True
    # APV_SystSettings.round_up_field_dimensions = True
    APV_SystSettings.scene_camera_dicts[
        'top_down']['horizontal_view_angle'] = 55
    APV_SystSettings.scene_camera_dicts[
        'top_down']['vertical_view_angle'] = 50

    APV_SystSettings.ground_scan_margin_x = 0  # 16  # -3
    APV_SystSettings.ground_scan_margin_y = 0  # 4  # -32
    APV_SystSettings.ground_scan_shift_x = 0  # -32
    APV_SystSettings.ground_scan_shift_y = 0  # -32

    # APV_SystSettings.module_form = 'checker_board'
    SimSettings.sim_name = (f'APV_Morschenich_{APV_SystSettings.module_form}'
                            f'res_{SimSettings.spatial_resolution}')
    weather_file = aiana.settings.user_paths.radiance_input_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    #
    imp.reload(aiana.classes.geometries_handler)
    imp.reload(aiana.classes.br_wrapper)
    # SimSettings.use_multi_processing = False

    APV_SystSettings.add_groundScanArea_as_object_to_scene = True

    aiana = aiana.classes.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        weather_file=weather_file,
    )

    aiana.run_raytracing_simulation()
    # #

    for hour in range(8, 21, 2):
        # for azimuth in range(180, 361, 30):
        SimSettings.sim_date_time = f'06-15_{hour}h'
        aiana = aiana.classes.br_wrapper.BR_Wrapper(
            SimSettings=SimSettings,
            APV_SystSettings=APV_SystSettings,
            weather_file=weather_file,
            # debug_mode=True
        )
        aiana.setup_br()
        # aiana.view_scene(view_name='total')
        aiana.run_raytracing_simulation()
        aiana.plot_ground_heatmap()

# #
import aiana
APV_SystSettings = aiana.settings.apv_systems.Default()
APV_SystSettings.scene_camera_dicts['total']
# #

aiana.plot_ground_heatmap()
# #
aiana.view_scene(
    view_name='top_down',
    view_type='parallel'
)
# #
if __name__ == '__main__':
    aiana.run_raytracing_simulation()
    # #
    aiana.plot_ground_heatmap()
    # #
    # show result data frame
    aiana.df_ground_results
    # #
    evalObj.evaluate_APV()


# #
