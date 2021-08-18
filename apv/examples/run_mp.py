# #
"""multi processing"""
if __name__ == '__main__':
    from pathlib import Path
    from apv.settings import UserPaths
    import importlib as imp
    import os

    # custom
    import apv
    imp.reload(apv.settings)
    imp.reload(apv.br_wrapper)

    simSettings = apv.settings.Simulation()

    # simSettings.only_ground_scan = False
    # simSettings.ray_tracing_accuracy = 'high'

    simSettings.sim_date_time = '06-15_11h'
    simSettings.checker_board = False
    simSettings.spatial_resolution = 5
    simSettings.sky_gen_mode = 'gendaylit'
    simSettings.sim_name = 'mp'

    weather_file = UserPaths.bifacial_radiance_files_folder / \
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
    imp.reload(apv.utils.plots)
    imp.reload(apv.br_wrapper)
    brObj = apv.br_wrapper.BifacialRadianceObj(
        SimSettings=simSettings,
        weather_file=weather_file
    )
    brObj.plot_ground_insolation()

# #
