# #
from aiana.classes.aiana_main import AianaMain
from aiana.classes.util_classes.settings_handler import Settings

if __name__ == '__main__':
    settings = Settings()
    settings.sim.study_sub_folderName = 'test7'
    settings.sim.spatial_resolution = 0.5
    settings.sim.hours = list(range(3, 15))  # only morning
    am = AianaMain(settings)

    #am.create_and_view_octfile_for_SceneInspection()
##
if __name__ == '__main__':
    for month in [4, 8]:
        am.update_simTime(month=month)
        am.simulate_and_evaluate(  # skip_sim_for_existing_results=True
        )
# #
