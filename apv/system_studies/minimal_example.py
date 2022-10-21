# #
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.util_classes.settings_handler import Settings

if __name__ == '__main__':
    settings = Settings()
    settings.sim.study_sub_folderName = 'test5'
    settings.sim.spatial_resolution = 0.5
    settings.sim.hours = list(range(3, 15))  # only morning
    brObj = BR_Wrapper(settings)

    brObj.create_and_view_octfile_for_SceneInspection()
# #
if __name__ == '__main__':
    for month in [4, 8]:
        brObj.update_simTime(month=month)
        brObj.simulate_and_evaluate(skip_sim_for_existing_results=True)
# #
