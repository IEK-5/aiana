# #
from aiana.classes.aiana_main import AianaMain
from aiana.classes.util_classes.settings_handler import Settings

if __name__ == '__main__':
    settings = Settings()
    settings.sim.study_sub_folderName = 'test5'
    settings.sim.spatial_resolution = 0.5
    settings.sim.hours = list(range(3, 15))  # only morning
    aiana = AianaMain(settings)

    aiana.create_and_view_octfile_for_SceneInspection()
# #
if __name__ == '__main__':
    for month in [4, 8]:
        aiana.update_simTime(month=month)
        aiana.simulate_and_evaluate(skip_sim_for_existing_results=True)
# #
