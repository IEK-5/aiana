# #
import copy
from typing import Literal
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.util_classes.settings_handler import Settings
from apv.settings.sim_settings import SimSettings_ForTesting
from apv.settings.apv_system_settings import APV_Syst_InclinedTables_S_Morschenich
from apv.settings.apv_system_settings import APV_ForTesting


class Tester():
    """methods to loop through config settings step by step while
    resetting the other settings to the default_settings"""

    def __init__(
            self, default_settings: Settings = None, open_oct_viewer=False):

        if default_settings is None:
            self.default_settings = Settings()
            # overwrites by test setting-presets:
            self.default_settings.apv = APV_ForTesting()
            self.default_settings.sim = SimSettings_ForTesting()
            self.default_settings.update_sim_dt_and_paths()
        else:
            self.default_settings = copy.deepcopy(default_settings)
        self._set_current_to_default_settings()

        self.sim_SettingNames = list(self.settings.sim.__dict__)
        self.apv_settingNames = list(self.settings.apv.__dict__)
        self.view_settingNames = list(self.settings.view.__dict__)

    def change_default_Setting(self, attr_name: str, value) -> None:
        parentObj = self._find_out_attr_parentObj(attr_name)
        setattr(parentObj, attr_name, value)
        print(parentObj, attr_name, 'set to', value)
        self._set_default_to_current_settings()

    # =========================================================================

    def test_inverted_bool_settings(self, bool_setting_names: list, **kwargs):
        """tests the attributes in bool_setting_names list
            one by one with inverted values.

            bool_setting_names list of strings being the names of the bool
            attributes that should be tested with inverted values.
        """
        for attr_name in bool_setting_names:
            parentObj = self._find_out_attr_parentObj(attr_name)
            currentValue = getattr(parentObj, attr_name)
            print(attr_name, 'was set to', currentValue,
                  '-> testing', not currentValue, 'now...')
            setattr(parentObj, attr_name, not currentValue)
            self._view_oct_then_resetSettings(**kwargs)
        return

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

    def test_listItems_seperately(
            self, setting_name: str, test_list: list, **kwargs):
        """applies the test_list items one by one onto the settings-attribute
        having settings_name as name.
        """
        parentObj = self._find_out_attr_parentObj(setting_name)
        for item in test_list:
            setattr(parentObj, setting_name, item)
            self._view_oct_then_resetSettings(**kwargs)

    # =========================================================================

    def _find_out_attr_parentObj(self, attr_name: str):
        if attr_name in self.apv_settingNames:
            return self.settings.apv
        if attr_name in self.sim_SettingNames:
            return self.settings.sim
        if attr_name in self.view_settingNames:
            return self.settings.view
        else:
            raise Exception(attr_name, " not in apv, sim or view settings.")

    def _view_oct_then_resetSettings(self, **kwargs):
        BR_Wrapper(self.settings).create_and_view_octfile_for_SceneInspection(
            **kwargs
        )
        self._set_current_to_default_settings()

    def _set_current_to_default_settings(self):
        self.settings = copy.deepcopy(self.default_settings)
        self.settings.update_sim_dt_and_paths()

    def _set_default_to_current_settings(self):
        self.default_settings = copy.deepcopy(self.settings)
        self.default_settings.update_sim_dt_and_paths()


# #
if __name__ == "__main__":
    testObj = Tester()

    # #
    settingsDict: dict = {}
    for parentObj in [
            testObj.settings.sim, testObj.settings.apv, testObj.settings.view]:
        settingsDict.update(parentObj.__dict__)
    print(settingsDict.keys())
    # #
    bool_attrs_names = [
        attr for attr in settingsDict.keys() if type(settingsDict[attr]) == Literal]
    bool_attrs_names
    # #
    bool_attrs_names = ['use_acceleradRT_view']
    testObj.test_inverted_bool_settings(bool_attrs_names)

# #
