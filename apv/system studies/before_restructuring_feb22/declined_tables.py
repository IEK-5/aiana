# #
"""declined tables"""

if __name__ == '__main__':
    from pathlib import Path
    import importlib as imp
    import apv
    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)

    SimSettings = apv.settings.sim_settings.Simulation()
    # APV_SystSettings = apv.settings.apv_systems.Default()
    APV_SystSettings = \
        apv.settings.apv_systems.APV_Syst_InclinedTables_Juelich()

    # ### often changed settings:  ####
    # SimSettings.sim_date_time = '06-15_12h'
    SimSettings.spatial_resolution = 1
    # SimSettings.sky_gen_mode = 'gendaylit'

    SimSettings.sim_name = 'declined_tables_and_glassbox'
    SimSettings.use_multi_processing = False
    brObj = apv.classes.br_wrapper.BR_Wrapper(SimSettings, APV_SystSettings)
    brObj.setup_br()
    # #
    brObj.view_scene(
        # view_name='top_down',
        # view_type='parallel'
    )
# #
if __name__ == '__main__':
    brObj.run_raytracing_simulation()
    # #
    # plot existing data (simulation cell does not need to be repeated)
    brObj.plot_ground_heatmap()
    # #
    # show result data frame
    brObj.df_ground_results

# #
