# #
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.util_classes.settings_grouper import Settings

if __name__ == '__main__':
    settings = Settings()
    settings.sim.study_name = f'std'
    settings.sim.spatial_resolution = 0.25
    settings.sim.time_step_in_minutes = 6
    # optional accelerad if installed:
    settings.sim.use_acceleradRT_view = True
    settings.sim.use_accelerad_GPU_processing = True

    settings.apv.sceneDict['nRows'] = 5
    settings.apv.mountingStructureDict.update({
        'n_apv_system_clones_in_x': 2,
        'n_apv_system_clones_in_negative_x': 2}
    )

    brObj = BR_Wrapper(settings)
    # #
    brObj.create_and_view_octfile()
    # #
    brObj.simulate_and_evaluate()
    # #
    brObj.plotterObj.ground_heatmap(cm_unit='shadow_depth')
