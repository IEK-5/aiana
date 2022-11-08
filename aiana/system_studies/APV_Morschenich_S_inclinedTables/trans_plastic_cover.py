# #
from aiana.classes.aiana_main import AianaMain
from aiana.classes.util_classes.settings_handler import Settings
from aiana.settings.apv_system_settings import APV_Syst_InclinedTables_S_Morschenich
if __name__ == '__main__':
    settings = Settings()
    settings.sim.study_sub_folderName = 'trans_plastic_cover'
    settings.sim.spatial_resolution = 10.5
    settings.sim.hours = list(range(3, 15))  # only morning

    #settings.apv = APV_Syst_InclinedTables_S_Morschenich()
    settings.apv.add_trans_plastic_between_modules = True
    settings.apv.glass_modules = False

    aiana = AianaMain(settings)
    ##
    aiana.create_and_view_octfile_for_SceneInspection()
# #
if __name__ == '__main__':
    for month in [4, 8]:
        aiana.update_simTime(month=month)
        aiana.simulate_and_evaluate(skip_sim_for_existing_results=True)
