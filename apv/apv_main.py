# #
"""apv main"""

if __name__ == '__main__':
    from pathlib import Path
    import importlib as imp
    import apv
    imp.reload(apv.br_wrapper)

    simSettings = apv.settings.Simulation()

    # ### often changed settings:  ####
    # simSettings.only_ground_scan = False
    # use_multi_processing = False
    # simSettings.add_mounting_structure = False
    simSettings.sim_date_time = '06-15_11h'
    simSettings.spatial_resolution = 1
    simSettings.sky_gen_mode = 'gendaylit'
    simSettings.sim_name = 'APV_floating'
    # simSettings.module_form = 'EW_fixed'

    weather_file = apv.settings.UserPaths.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    brObj = apv.br_wrapper.BifacialRadianceObj(
        SimSettings=simSettings,
        weather_file=weather_file  # downloading automatically without this
    )
    # #
    brObj.view_scene(
        view_name='module_zoom'
    )
    # #
    brObj.run_raytracing_simulation()

    # plot existing data (simulation cell does not need to be repeated)
    brObj.plot_ground_insolation()

    # show result data frame
    brObj.df_ground_results

    # #
