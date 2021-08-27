# #
"""apv main"""

if __name__ == '__main__':
    from pathlib import Path
    import importlib as imp
    import apv
    imp.reload(apv.utils.radiance_geometries)
    imp.reload(apv.br_wrapper)

    SimSettings = apv.settings.simulation.Simulation()
    # APV_SystSettings = apv.settings.apv_systems.Default()
    APV_SystSettings = \
        apv.settings.apv_systems.Default()

    # ### often changed settings:  ####
    # SimSettings.only_ground_scan = False
    # use_multi_processing = False
    # SimSettings.add_mounting_structure = False
    SimSettings.sim_date_time = '06-15_11h'
    SimSettings.spatial_resolution = 1
    SimSettings.sky_gen_mode = 'gendaylit'
    SimSettings.sim_name = 'APV_floating'
    APV_SystSettings.module_form = 'std'
    APV_SystSettings.moduleDict['xgap'] = 0.1
    # APV_SystSettings.mounting_structure_type = 'declined_tables'
    # APV_SystSettings.sceneDict['nRows'] = 3
    APV_SystSettings.sceneDict['nMods'] = 6
    APV_SystSettings.sceneDict['azimuth'] = 180
    APV_SystSettings.ground_scan_margin_x = -3
    APV_SystSettings.ground_scan_margin_y = -32
    weather_file = apv.settings.user_pathes.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    brObj = apv.br_wrapper.BifacialRadianceObj(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        weather_file=weather_file,  # downloading automatically without this,
        debug_mode=True
    )
    brObj.setup_br()
    # #
    imp.reload(apv.utils.radiance_geometries)
    imp.reload(apv.br_wrapper)
    brObj._create_geometries(APV_SystSettings=APV_SystSettings)
    brObj.view_scene(
        view_name='top_down',
        view_type='parallel'
    )
    # #
    brObj.run_raytracing_simulation()
    # #

    # plot existing data (simulation cell does not need to be repeated)
    brObj.plot_ground_insolation()

    # show result data frame
    brObj.df_ground_results

    # #
