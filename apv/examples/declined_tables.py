# #
"""declined tables"""

if __name__ == '__main__':
    from pathlib import Path
    import importlib as imp
    import apv
    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)

    SimSettings = apv.settings.simulation.Simulation()
    # APV_SystSettings = apv.settings.apv_systems.Default()
    APV_SystSettings = \
        apv.settings.apv_systems.APV_Syst_InclinedTables_Juelich()

    # ### often changed settings:  ####
    # SimSettings.sim_date_time = '06-15_12h'
    SimSettings.spatial_resolution = 0.5
    # SimSettings.sky_gen_mode = 'gendaylit'

    SimSettings.sim_name = 'declined_tables_and_glassbox'

    weather_file = apv.settings.user_pathes.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    brObj = apv.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        weather_file=weather_file  # downloading automatically without this,
    )
    brObj.setup_br()
    # #
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
