# #
if __name__ == '__main__':
    from pathlib import Path
    import apv

    SimSettings = apv.settings.simulation.Simulation()
    APV_SystSettings = \
        apv.settings.apv_systems.Default()

    weather_file = apv.settings.user_pathes.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    brObj = apv.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        weather_file=weather_file  # downloading automatically without this
    )
    # #
    brObj.setup_br()
    # #
    brObj.view_scene(
        view_name='top_down', view_type='parallel'
    )
    # #
    brObj.run_raytracing_simulation()
    # #
    # plot existing data (simulation cell does not need to be repeated)
    brObj.plot_ground_insolation()
    # TODO why is there a darker line at the top?
    # #
    brObj.plot_ground_insolation(cm_unit='Shadow-Depth')
    # show result data frame
    brObj.df_ground_results

# #
