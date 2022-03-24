# #
if __name__ == '__main__':
    import apv

    SimSettings = apv.settings.sim_settings.Simulation()
    SimSettings.sim_name = 'inclined_tables_and_glassbox'
    SimSettings.spatial_resolution = 1
    APV_SystSettings = \
        apv.settings.apv_systems.APV_Syst_InclinedTables_Juelich()

    brObj = apv.classes.br_wrapper.BR_Wrapper(SimSettings, APV_SystSettings)
    brObj.setup_br()

    # #
    brObj.view_scene()
# #
if __name__ == '__main__':
    brObj.run_raytracing_simulation()
    # #
    brObj.plot_ground_heatmap()
    # #
    brObj.plot_ground_heatmap(cm_unit='shadow_depth')
    # #
    # show result data frame
    brObj.df_ground_results
