# #
if __name__ == '__main__':
    import aiana

    SimSettings = aiana.settings.sim_settings.Simulation()
    SimSettings.sim_name = 'inclined_tables_and_glassbox'
    SimSettings.spatial_resolution = 1
    APV_SystSettings = \
        aiana.settings.apv_systems.APV_Syst_InclinedTables_Juelich()

    aiana = aiana.classes.br_wrapper.BR_Wrapper(SimSettings, APV_SystSettings)
    aiana.setup_br()

    # #
    aiana.view_scene()
# #
if __name__ == '__main__':
    aiana.run_raytracing_simulation()
    # #
    aiana.plot_ground_heatmap()
    # #
    aiana.plot_ground_heatmap(cm_unit='shadow_depth')
    # #
    # show result data frame
    aiana.df_ground_results
