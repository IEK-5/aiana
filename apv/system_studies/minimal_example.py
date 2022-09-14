# #
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.util_classes.settings_handler import Settings
from apv.settings.user_paths import UserPaths

if __name__ == '__main__':
    settings = Settings()
    settings.sim.study_name = 'test4'
    settings.sim.spatial_resolution = 1
    settings.sim.hours = list(range(3, 15))  # only morning

    brObj = BR_Wrapper(settings)
    # #
    brObj.create_and_view_octfile_for_SceneInspection()
# #
if __name__ == '__main__':
    for month in [6, 8]:
        brObj.update_time(month=month)
        brObj.simulate_and_evaluate(skip_sim_for_existing_results=True)
    # TODO
    # typical day per month ohne tmy, was passiert da
# #
