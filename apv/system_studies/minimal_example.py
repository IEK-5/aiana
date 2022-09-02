# #
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.util_classes.settings_handler import Settings
from apv.settings.apv_system_settings import APV_Syst_InclinedTables_S_Morschenich

if __name__ == '__main__':
    settings = Settings()
    settings.sim.spatial_resolution = 0.4
    # optional accelerad if installed:
    settings.view.use_acceleradRT_view = True
    settings.sim.use_accelerad_GPU_processing = True
    # settings.apv = APV_Syst_InclinedTables_S_Morschenich()
    # settings.apv.sceneDict['nRows']=6
    settings.apv.glass_modules = True
    settings.apv.mountingStructureDict['n_apv_system_clones_in_x'] = 2
    #settings.apv.mountingStructureType = 'framed_single_axes_ridgeRoofMods'
    #settings.apv.moduleDict['numpanels'] = 5

    brObj = BR_Wrapper(settings)
    brObj.create_and_view_octfile_for_SceneInspection()
    # #
    brObj.create_octfile_for_Simulation()
    for hour in [10, 16]:
        # set time with leading zeros for a correct file order
        settings.sim.sim_date_time = f'06-15_{hour:02}:00'
        brObj.update_timeStep_and_sky(settings)
        brObj.simulate_and_evaluate()
        brObj.plotterObj.ground_heatmap(north_arrow_xy_posi=(-0.44, 1.2),
                                        plot_dpi=600)
# #
