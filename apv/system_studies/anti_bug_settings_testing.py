# #
from apv.settings.apv_systems import APV_Syst_InclinedTables_S_Morschenich

if __name__ == '__main__':
    """#NOTE regardless of cell-seperators (# #) this py file will be loaded
    completely and run multiple times due to multiprocessing. It wont work
    if there is anything unclean added below."""
    from apv.classes.util_classes.settings_grouper import Settings
    from apv.classes.br_wrapper import BR_Wrapper

    settings = Settings()
    settings.sim.sim_date_time = '06-15_12:00'
    settings.sim.spatial_resolution = 0.1
    settings.sim.use_typDay_perMonth_for_irradianceCalculation = False
    settings.sim.use_CPU_multi_processing = False

    settings.apv = APV_Syst_InclinedTables_S_Morschenich()
    settings.sim.use_acceleradRT_view = True
    settings.sim.use_accelerad_GPU_processing = True

    """    brObj = BR_Wrapper(settings)
    brObj.octFileObj.create_octfile()

    brObj.octFileObj.view_octfile(
        view_name='top_down', view_type='parallel'
    )
    """
    # #
    BR_Wrapper(settings).create_and_view_octfile()
    # #

    """sceneDict"""
    for nMods in [10, 4]:
        settings.apv.sceneDict['nMods'] = nMods
        BR_Wrapper(settings).create_and_view_octfile()
    # #
    for nRows in [5, 2]:
        settings.apv.sceneDict['nRows'] = nRows
        BR_Wrapper(settings).create_and_view_octfile()
    # #
    for tilt in [70, 20]:
        settings.apv.sceneDict['tilt'] = tilt
        BR_Wrapper(settings).create_and_view_octfile()
    # #
    for pitch in [20, 10]:
        settings.apv.sceneDict['pitch'] = pitch
        BR_Wrapper(settings).create_and_view_octfile()
    # #
    for hub_height in [12, 4]:
        settings.apv.sceneDict['hub_height'] = hub_height
        BR_Wrapper(settings).create_and_view_octfile()
    # #
    for azimuth in [90, 270, 180]:
        settings.apv.sceneDict['azimuth'] = azimuth
        BR_Wrapper(settings).create_and_view_octfile()

    # #

    # settings.apv.n_apv_system_clones_in_x = 2
    # settings.apv.add_groundScanArea_as_object_to_scene = True

    for structure_type in ['none', 'declined_tables', 'framed_single_axes']:
        settings.apv.mounting_structure_type = structure_type
        brObj = BR_Wrapper(settings)
        brObj.create_and_view_octfile()
    # #

# #
if __name__ == '__main__':
    brObj = BR_Wrapper(settings)
    brObj.octFileObj.create_octfile()
    # TODO how can create_oct_file be made skipable for sim to work,
    # if file already existing?
    # (TypeError: 'NoneType' object is not subscriptable)
    brObj.simulate_and_evaluate()
    # #
    brObj = BR_Wrapper(settings)
    brObj.plotterObj.ground_heatmap(  # cm_unit='shadow_depth'
    )
    # #
    # show result data frame
    brObj.evaluatorObj.df_ground_results
