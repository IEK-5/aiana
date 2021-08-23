# #
"""apv main"""

if __name__ == '__main__':
    from pathlib import Path
    import importlib as imp
    import apv
    imp.reload(apv.br_wrapper)

    SimSettings = apv.settings.Simulation()
    APV_SystSettings = apv.settings.APV_System()

    # ### often changed settings:  ####
    # SimSettings.only_ground_scan = False
    # use_multi_processing = False
    # SimSettings.add_mounting_structure = False
    SimSettings.sim_date_time = '06-15_11h'
    SimSettings.spatial_resolution = 5
    SimSettings.sky_gen_mode = 'gendaylit'
    SimSettings.sim_name = 'APV_floating'
    # APV_SystSettings.module_form = 'cell_level'

    weather_file = apv.settings.UserPaths.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    brObj = apv.br_wrapper.BifacialRadianceObj(
        SimSettings=SimSettings,
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
