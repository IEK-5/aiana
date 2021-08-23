# #
"""debugging low res"""
if __name__ == '__main__':
    from pathlib import Path
    import importlib as imp

    import apv
    imp.reload(apv.settings)
    imp.reload(apv.br_wrapper)

    simSettings = apv.settings.simulation.Simulation()

    # simSettings.only_ground_scan = False
    # use_multi_processing = False

    simSettings.sim_date_time = '06-15_11h'
    simSettings.spatial_resolution = 5
    simSettings.sky_gen_mode = 'gendaylit'
    simSettings.sim_name = 'APV_floating'

    weather_file = apv.settings.user_pathes.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    brObj = apv.br_wrapper.BifacialRadianceObj(
        SimSettings=simSettings,
        weather_file=weather_file
        # without this, download happens automatically
    )
    # #
    brObj.view_scene(
        view_name='module_zoom'
    )
# #
# if __name__ == '__main__': needed again here due to the vs code cells,
# otherwise multi processing will excecute the cells above again causing
# freezing because rad file is accessed multiple times, which is
# not allowed by the OS.
if __name__ == '__main__':
    brObj.run_raytracing_simulation()

    # show results
    brObj.df_ground_results
    # #
    # plot existing data (simulation cell does not need to be repeated)
    brObj = apv.br_wrapper.BifacialRadianceObj(
        SimSettings=simSettings,
        weather_file=weather_file
    )
    imp.reload(apv.utils.plots)
    imp.reload(apv.br_wrapper)
    brObj.plot_ground_insolation()

# #
