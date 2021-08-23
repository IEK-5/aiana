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
        apv.settings.apv_systems.APV_Syst_InclinedTables_Juelich()

    # ### often changed settings:  ####
    # SimSettings.only_ground_scan = False
    # use_multi_processing = False
    # SimSettings.add_mounting_structure = False
    SimSettings.sim_date_time = '06-15_11h'
    SimSettings.spatial_resolution = 5
    SimSettings.sky_gen_mode = 'gendaylit'
    SimSettings.sim_name = 'APV_floating'
    APV_SystSettings.module_form = 'std'
    APV_SystSettings.mounting_structure_type = 'declined_tables'
    # APV_SystSettings.sceneDict['nRows'] = 3
    # APV_SystSettings.sceneDict['nMods'] = 6

    weather_file = apv.settings.user_pathes.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    brObj = apv.br_wrapper.BifacialRadianceObj(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        weather_file=weather_file  # downloading automatically without this
    )
    # #
    brObj.view_scene(
        # view_name='module_zoom'
    )
    # #
    brObj.run_raytracing_simulation()

    # plot existing data (simulation cell does not need to be repeated)
    brObj.plot_ground_insolation()

    # show result data frame
    brObj.df_ground_results

    # #
