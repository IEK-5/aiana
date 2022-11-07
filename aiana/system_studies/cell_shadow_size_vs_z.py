# #
"""
    teste spaltgröße nicht nur im gebäude sondern auch unter freiem himmel
    nicht dass das glas im bürogebäude einfluss hat...
    """
from aiana.classes.aiana_main import Aiana
from aiana.classes.util_classes.settings_handler import Settings
from aiana.settings.apv_system_settings import APV_ForTesting

if __name__ == '__main__':
    settings = Settings()

    settings.sim.spatial_resolution = 0.005
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
        aiana = Aiana(settings)
        # aiana.create_and_view_octfile_for_SceneInspection()
##
        aiana.create_octfile_for_Simulation(add_groundScanArea=True
                                            )
        aiana.simulatorObj.run_raytracing_simulation()
        aiana.evaluatorObj.rename_and_add_result_columns()
        # aiana.simulate_and_evaluate()
        aiana.plotterObj.ground_heatmap(north_arrow_xy_posi=(-0.44, 1.2),
                                        plot_dpi=600,
                                        plot_title=f'z = {z}')
# #
aiana.settings._paths.inst_csv_parent_folder
