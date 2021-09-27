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
    APV_SystSettings = apv.settings.apv_systems.Default()
    evalObj = apv.utils.APV_evaluation.Evaluate_APV(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings
    )
    # ### often changed settings:  ####
    SimSettings.spatial_resolution = 1
    print(SimSettings.irradiance_data_source)
    # Insert start end-date of the year as [month,day,hour]
    SimSettings.sky_gen_mode = 'gendaylit'
    APV_SystSettings.moduleDict['xgap'] = 0.02
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
    # APV_SystSettings.round_up_field_dimensions = True
    APV_SystSettings.scene_camera_dicts[
        'top_down']['horizontal_view_angle'] = 55
    APV_SystSettings.scene_camera_dicts[
        'top_down']['vertical_view_angle'] = 50

    APV_SystSettings.ground_scan_margin_x = 0  # 16  # -3
    APV_SystSettings.ground_scan_margin_y = 0  # 4  # -32
    APV_SystSettings.ground_scan_shift_x = 0  # -32
    APV_SystSettings.ground_scan_shift_y = 0  # -32

    # APV_SystSettings.module_form = 'cell_level_checker_board'
    SimSettings.sim_name = (f'APV_Morschenich_{APV_SystSettings.module_form}'
                            f'res_{SimSettings.spatial_resolution}')
    weather_file = apv.settings.user_pathes.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    #
    imp.reload(apv.utils.GeometriesHandler)
    imp.reload(apv.br_wrapper)
    # SimSettings.use_multi_processing = False

    APV_SystSettings.add_groundScanArea_as_object_to_scene = True

    brObj = apv.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        weather_file=weather_file,
    )

    brObj.run_raytracing_simulation()
    # #

    for hour in range(8, 21, 2):
        # for azimuth in range(180, 361, 30):
        SimSettings.sim_date_time = f'06-15_{hour}h'
        brObj = apv.br_wrapper.BR_Wrapper(
            SimSettings=SimSettings,
            APV_SystSettings=APV_SystSettings,
            weather_file=weather_file,
            # debug_mode=True
        )
        brObj.setup_br()
        # brObj.view_scene(view_name='total')
        brObj.run_raytracing_simulation()
        brObj.plot_ground_insolation()

# #
import apv
APV_SystSettings = apv.settings.apv_systems.Default()
APV_SystSettings.scene_camera_dicts['total']
# #

brObj.plot_ground_insolation()
# #
brObj.view_scene(
    view_name='top_down',
    view_type='parallel'
)
# #
if __name__ == '__main__':
    brObj.run_raytracing_simulation()
    # #
    brObj.plot_ground_insolation()
    # #
    # show result data frame
    brObj.df_ground_results
    # #
    evalObj.evaluate_APV()


# #
