# #
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.util_classes.settings_grouper import Settings

if __name__ == '__main__':
    settings = Settings()
    settings.sim.spatial_resolution = 0.2
    # optional accelerad if installed:
    settings.sim.use_acceleradRT_view = True
    settings.sim.use_accelerad_GPU_processing = True
    settings.apv.module_form = 'cell_level_checker_board'
    settings.apv.module_form = 'roof_for_EW'
    settings.apv.glass_modules = True
    settings.apv.mountingStructureDict['n_apv_system_clones_in_x'] = 1
    brObj = BR_Wrapper(settings)

    brObj.create_and_view_octfile(add_groundScanArea=False)
    # #
    brObj.create_and_view_octfile()
    # #
    brObj.simulate_and_evaluate()
    # #
    brObj.plotterObj.ground_heatmap(cm_unit='shadow_depth')
