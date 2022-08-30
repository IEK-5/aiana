# #
import copy
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.util_classes.settings_grouper import Settings
from apv.settings.sim_settings import SimSettings_ForTesting
from apv.settings.apv_systems import APV_Syst_InclinedTables_S_Morschenich
from apv.settings.apv_systems import APV_ForTesting


class Tester():
    """methods to loop through config settings step by step while
    resetting the other settings to the default_settings"""

    def __init__(self, default_settings: Settings = None):
        if default_settings is None:
            self.default_settings = Settings()
            self.default_settings.apv = APV_ForTesting()
            self.default_settings.sim = SimSettings_ForTesting()
        else:
            self.default_settings = copy.deepcopy(default_settings)
        self.set_settings_to_default()

    def set_settings_to_default(self):
        self.settings = copy.deepcopy(self.default_settings)

    def change_default_apvSettings(self, name: str, value) -> None:
        setattr(self.default_settings.apv, name, value)
        print(f'APV setting {name} set to {value}.')
        self.set_settings_to_default()

    def change_default_simSettings(self, name: str, value) -> None:
        setattr(self.default_settings.sim, name, value)
        print(f'Simulation setting {name} set to {value}.')
        self.set_settings_to_default()

    def _view_oct_then_resetSettings(self, **kwargs):
        BR_Wrapper(self.settings).create_and_view_octfile_for_SceneInspection(
            **kwargs
        )
        self.set_settings_to_default()

    def view_in_rvu_then_in_acceleradRT(self):
        # without acceleradRT
        self.settings.sim.use_acceleradRT_view = False
        BR_Wrapper(self.settings).create_and_view_octfile_for_SceneInspection()
        # with acceleradRT
        self.settings.sim.use_acceleradRT_view = True
        BR_Wrapper(self.settings).create_and_view_octfile_for_SceneInspection()

    def test_dictItems_seperately(
            self, settings_dict_name: str, test_dict: dict, **kwargs):
        """Tests passed settings.apv dictionary, but not all
        items at once. Instead, each item is tested in a loop
        seperately with otherwise default settings as written in
        the class SimSettings_ForTesting and is set to default afterwards.

        Args:
            settings_dict_name (str): name of the dictionary in the settings,
            whichs items will be tested seperately with the values
            of test_dict (dict).
            test_dict (dict):

            **kwargs: add_groundScanArea: bool = True,
            add_sensor_vis: bool = True,
            add_NorthArrow: bool = True,
            view_name: str = 'total' or 'top_down'
        """

        default_dict: dict = getattr(
            self.default_settings.apv, settings_dict_name)

        for key in test_dict:
            if key not in default_dict:
                raise KeyError(
                    f'{key} not found in {settings_dict_name}. '
                    f'Valid keys are {list(default_dict.keys())}.'
                )
            temp_dict = default_dict.copy()
            temp_dict[key] = test_dict[key]
            setattr(self.settings.apv, settings_dict_name, temp_dict)

            self._view_oct_then_resetSettings(**kwargs)

    def test_listItems_seperately(self, settings_list_name: str,
                                  test_list: dict):
        """similar to test_dict_items_seperately"""
        for item in test_list:

            default_list: dict = getattr(
                self.settings.apv, settings_list_name)

            if item not in default_list:
                raise KeyError(
                    f'{item} not found in {settings_list_name}. '
                    f'Valid items are {default_list}.'
                )
            setattr(self.settings.apv, settings_list_name, item)

            self._view_oct_then_resetSettings()


if __name__ == '__main__':
    testerObj = Tester()
    # #
    # view system with default test settings
    BR_Wrapper(testerObj.settings).create_and_view_octfile_for_SceneInspection()
    # #
    # test apv system settings
    testerObj.test_dictItems_seperately("sceneDict", {'tilt': 70,
                                                      'pitch': 20,
                                                      'hub_height': 12,
                                                      'nMods': 10,
                                                      'nRows': 5})
    # #
    # azimuth
    # 14:00 -> sunposition 13:30 for hourly time_step = noon
    testerObj.change_default_simSettings('sim_date_time', '06-15_14:00')
    for azimuth in [90, 180, 270]:
        testerObj.test_dictItems_seperately("sceneDict", {'azimuth': azimuth},
                                            view_name="top_down")

    # #
    testerObj.test_dictItems_seperately("moduleDict", {'x': 0.5,
                                                       'y': 1,
                                                       'xgap': 1,
                                                       'ygap': 1,
                                                       'zgap': 1,
                                                       'numpanels': 4})
    # #
    testerObj.test_dictItems_seperately("gScanAreaDict",
                                        {'ground_scan_margin_x': 9,
                                         'ground_scan_margin_y': 9,
                                         'ground_scan_shift_x': 9,
                                         'ground_scan_shift_y': 9,
                                         'round_up_scan_edgeLengths': True
                                         })
    # #
    # test module forms with and without glass
    for glass in [True, False]:
        testerObj.change_default_apvSettings("glass_modules", glass)
        testerObj.test_listItems_seperately("module_form", ['std', 'cell_gaps',
                                                            # 'checker_board',
                                                            # 'roof_for_EW',
                                                            # 'cell_gaps_roof_for_EW' # BUG !
                                                            ])

    # #
    # mounting structure
    module_to_post_distance_x_dict = {
        'framed_single_axes': 0.5,
        'inclined_tables': -0.5  # to avoid modules floating between posts
    }
    for mountingStructureType in module_to_post_distance_x_dict:
        testerObj.change_default_apvSettings(
            "mountingStructureType", mountingStructureType)

        testerObj.default_settings.apv.mountingStructureDict[
            'module_to_post_distance_x'] = \
            module_to_post_distance_x_dict[mountingStructureType]
        testerObj.set_settings_to_default()

        testerObj.test_dictItems_seperately(
            "mountingStructureDict",
            {
                'n_apv_system_clones_in_x': 1,
                'n_apv_system_clones_in_negative_x': 1,
                'material': 'black',
                'post_thickness_x': 1,
                'post_thickness_y': 1,
                'n_post_x': 3,
                'post_distance_x': 3,
                'inner_table_post_distance_y': 0.5,  # only used by inclined_table
            }
        )

    # #
    # test and time updateSkyOnly for Morschenich APV and view scene

    import pytictoc
    tictoc = pytictoc.TicToc()

    for updateSk in [False, True]:
        testerObj.settings.apv = APV_Syst_InclinedTables_S_Morschenich()
        brObj = BR_Wrapper(testerObj.settings)
        tictoc.tic()
        brObj.create_octfile(update_sky_only=updateSk)
        tictoc.toc()
        print('=================================')
    brObj.octFileObj.view_octfile()

    # #

    # #
    testerObj.view_in_rvu_then_in_acceleradRT()

    # #
    # settings.apv.n_apv_system_clones_in_x = 2
