from apv.classes.br_wrapper import BR_Wrapper
from apv.anti_bug_testing.tester_class import Tester
from apv.settings.apv_system_settings import APV_Syst_InclinedTables_S_Morschenich

if __name__ == '__main__':
    testerObj = Tester(open_oct_viewer=True)
    # oct_viewer type
    testerObj.change_default_Setting

    def view_in_rvu_then_in_acceleradRT(self):
        # without acceleradRT
        self.settings.view.use_acceleradRT_view = False
        BR_Wrapper(self.settings).create_and_view_octfile_for_SceneInspection()
        # with acceleradRT
        self.settings.view.use_acceleradRT_view = True
        BR_Wrapper(self.settings).create_and_view_octfile_for_SceneInspection()
