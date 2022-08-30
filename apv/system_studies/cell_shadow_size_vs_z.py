# #
"""
    teste spaltgröße nicht nur im gebäude sondern auch unter freiem himmel
    nicht dass das glas im bürogebäude einfluss hat...
    """
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.util_classes.settings_grouper import Settings
from apv.settings.apv_systems import APV_ForTesting

if __name__ == '__main__':
    settings = Settings()

    settings.sim.spatial_resolution = 0.005
    settings.sim.use_acceleradRT_view = True
    settings.sim.use_accelerad_GPU_processing = True

    settings.apv = APV_ForTesting()
    settings.apv.module_form = 'cell_gaps'
    # TODO setting ground_scan_margin_x to -3 still draws green area, but not red sensors
    settings.apv.gScanAreaDict['ground_scan_margin_x'] = -2
    settings.apv.gScanAreaDict['ground_scan_margin_y'] = -6
    settings.apv.gScanAreaDict['ground_scan_shift_x'] = -2
    settings.apv.gScanAreaDict['ground_scan_shift_y'] = -4
    # #
if __name__ == '__main__':
    for z in [0, 5]:
        settings.sim.RadSensors_z_params['zstart'] = z
        settings.sim.results_subfolder = f'z_test/z {z}'
        brObj = BR_Wrapper(settings)
        # brObj.create_and_view_octfile_for_SceneInspection()
##
        brObj.create_octfile_for_Simulation(add_groundScanArea=True
                                            )
        brObj.simulatorObj.run_raytracing_simulation()
        brObj.evaluatorObj.rename_and_add_result_columns()
        # brObj.simulate_and_evaluate()
        brObj.plotterObj.ground_heatmap(north_arrow_xy_posi=(-0.44, 1.2),
                                        plot_dpi=600,
                                        plot_title=f'z = {z}')
# #
brObj.settings.paths.csv_parent_folder
