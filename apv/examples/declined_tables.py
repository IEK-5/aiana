# #
"""apv main"""

if __name__ == '__main__':
    from pathlib import Path
    import importlib as imp
    import apv
    imp.reload(apv.utils.GeometriesHandler)
    imp.reload(apv.br_wrapper)

    SimSettings = apv.settings.simulation.Simulation()
    # APV_SystSettings = apv.settings.apv_systems.Default()
    APV_SystSettings = \
        apv.settings.apv_systems.APV_Syst_InclinedTables_Juelich()

    # ### often changed settings:  ####
    # SimSettings.only_ground_scan = False
    # use_multi_processing = False
    # SimSettings.add_mounting_structure = False
    SimSettings.sim_date_time = '06-15_12h'
    SimSettings.spatial_resolution = 1
    SimSettings.sky_gen_mode = 'gendaylit'
    SimSettings.sim_name = 'APV_floating'

    weather_file = apv.settings.user_pathes.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    brObj = apv.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        weather_file=weather_file,  # downloading automatically without this,
        debug_mode=True
    )
    brObj.setup_br()
    # #
    # TODO if this cell is executed to debug the scene,
    # to run a simulation one has to restart session and skip this cell
    # to avoid an error, how to fix?
    imp.reload(apv.utils.GeometriesHandler)
    imp.reload(apv.br_wrapper)

    APV_SystSettings.round_up_field_dimensions = False

    APV_SystSettings.scene_camera_dicts['top_down']['horizontal_view_angle'] = 50
    APV_SystSettings.scene_camera_dicts['top_down']['vertical_view_angle'] = 40

    for azimuth in [225]:

        APV_SystSettings.sceneDict['azimuth'] = azimuth
        brObj._create_geometries(
            APV_SystSettings=APV_SystSettings
        )
        brObj.view_scene(
            # view_name='top_down',
            # view_type='parallel'
        )
    # #
    brObj.run_raytracing_simulation()
    # #

    # plot existing data (simulation cell does not need to be repeated)
    brObj.plot_ground_insolation()

    # show result data frame
    brObj.df_ground_results
