# #
if __name__ == '__main__':
    """#NOTE regardless of cell-seperators (# #) this py file will be loaded
    completely and run multiple times due to multiprocessing. It wont work
    if there is anything unclean added below."""
    from apv.classes.util_classes.settings_grouper import Settings
    from apv.classes.br_wrapper import BR_Wrapper

    settings = Settings()
    settings.sim.sim_date_time = '06-15_08:00'
    settings.sim.spatial_resolution = 0.1
    settings.apv.sceneDict['nRows'] = 1
    settings.apv.n_apv_system_clones_in_x = 2
    settings.apv.add_groundScanArea_as_object_to_scene = True
    brObj = BR_Wrapper(settings)
    # #
    brObj.create_octfile()
    # #
    brObj.view_octfile(
        # view_name='top_down', view_type='parallel'
    )
# #
if __name__ == '__main__':

    # TODO how can create_oct_file be made skipable for sim to work,
    # if file already existing? (TypeError: 'NoneType' object is not subscriptable)
    brObj.simulate_and_evaluate()
    # #
    brObj.plotterObj.ground_heatmap(cm_unit='shadow_depth')
    # #
    # show result data frame
    brObj.evaluatorObj.df_ground_results
