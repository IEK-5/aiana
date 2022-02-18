# #
if __name__ == '__main__':
    """#NOTE regardless ov cell-seperators (# #) this py file will be loaded
    completely and run multiple times due to multiprocessing. It wont work
    if there is anything unclean added below."""
    from apv.classes.util_classes.settings_grouper import Settings
    from apv.classes.br_wrapper import BR_Wrapper

    settings = Settings()
    settings.sim.sim_date_time = '06-15_08:00'
    # settings.apv.sceneDict['nRows']=1
    brObj = BR_Wrapper(settings)


    settings.set_names_and_paths()
    print(settings.names.csv_fn)

    settings.sim.spatial_resolution = 0.2
    settings.apv.n_apv_system_clones_in_x = 2
    settings.apv.add_groundScanArea_as_object_to_scene = True
    brObj = BR_Wrapper(settings)


    brObj.create_oct_file()
    # #
    brObj.octFileObj.view_scene(
        #view_name='top_down', view_type='parallel'
    )
# #
if __name__ == '__main__':

    # TODO how can create_oct_file be made skipable for sim to work,
    # if file already existing?
    brObj.simulatorObj.run_raytracing_simulation()

    # #
    brObj.plot_ground_heatmap()

    # #

    """
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
        evalObj.evaluate_APV(SimSettings)
    """
