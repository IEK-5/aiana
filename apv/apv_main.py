# #
if __name__ == '__main__':
    import apv

    SimSettings = apv.settings.simulation.Simulation()
    SimSettings.spatial_resolution = 1
    APV_SystSettings = apv.settings.apv_systems.Default()
    brObj = apv.br_wrapper.BR_Wrapper(SimSettings, APV_SystSettings)
    brObj.setup_br()

    # #
    brObj.view_scene(
        view_name='top_down', view_type='parallel'
    )
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
# #
if __name__ == '__main__':
    evalObj = apv.classes.APV_evaluation.APV_Evaluation(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings
    )
    evalObj.evaluate_APV()
