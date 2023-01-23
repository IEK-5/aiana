""" This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>."""
# #
import copy
from datetime import datetime
from pathlib import Path
from typing import Literal
from aiana.classes.aiana_main import AianaMain
from aiana.classes.plotter import Plotter
from aiana.classes.util_classes.settings_handler import Settings
from aiana.settings.sim_settings import SimSettings_ForTesting
from aiana.settings.apv_system_settings \
    import APV_Syst_InclinedTables_S_Morschenich
from aiana.settings.apv_system_settings import APV_ForTesting
from aiana.utils import files_interface as fi
import pandas as pd
from aiana.utils.RMSE_MBE import calc_RMSE_MBE


class Tester():
    """Class containing methods to loop through config settings step by step
    while resetting the other settings to the default_settings.

    mode (optional): Defaults to 'test'
        (which means 1. simulate 2. check and plot difference to reference)
            alternative: 'create_reference'

    open_oct_viewer (bool, optional): to check scene creation for each set.
        Viewer needs to be closed manualy. Defaults to False.

    default_settings (Settings, optional): Defaults to None (constructing
        automatically based on setting files)

    run_simulation (bool, optional): Defaults to True, can be set False,
        if only viewing is of interest.
    """
    settings: Settings  # used by the next test view/simulation
    # (has the currently tested parameter changed)
    default_settings: Settings  # contains the default for the currently
    # tested (changed) parameter, to which the paramter is set back after
    # the parameter test

    df_test: pd.DataFrame  # set in load_df_test_and_df_ref
    df_ref: pd.DataFrame  # ""

    def __init__(
            self,
            default_settings: Settings = None,
            open_oct_viewer=False,
            run_simulation=True,
            mode: Literal[
                'create_reference', 'test'] = 'test'
    ):

        self.open_oct_viewer = open_oct_viewer
        self.run_simulation = run_simulation
        self.mode = mode

        if default_settings is None:
            self.default_settings = Settings()
            # overwrites by test setting-presets:
            self.default_settings.apv = APV_ForTesting()
            self.default_settings.sim = SimSettings_ForTesting()
            self.default_settings.update_sim_dt_and_paths()
        else:
            self.default_settings = copy.deepcopy(default_settings)
            # deepcopy so that the passed Obj stays unchanged

        if self.mode == 'create_reference':
            self.default_settings.sim.study_name += '/reference'
        elif self.mode == 'test':
            self.default_settings.sim.study_name += '/test'
            # testObj-specific paths ###########
            # mean of differences abs(reference - test) of
            # time-cumulative shadowDepth are stored to:
            cm_quantity = self.default_settings.sim.cm_quantity
            self.RMSE_MBE_csv_path: Path = \
                self.default_settings._paths.results_folder \
                / Path(f'difference/test_results_{cm_quantity}.csv')
            if not self.RMSE_MBE_csv_path.exists():
                header = \
                    'sub_study_name-test_date\tMBE\trelMBE\tRMSE\trelRMSE\n'
                fi.write_to_txt_file(self.RMSE_MBE_csv_path, header)
        else:
            raise Exception('mode has to be "create_reference" or "test".')

        # update _paths.results_folder:
        self.default_settings.update_sim_dt_and_paths()
        ######################
        self.overwrite_settings_by_default_settings()

        self.sim_SettingNames = list(self.settings.sim.__dict__)
        self.apv_settingNames = list(self.settings.apv.__dict__)
        self.view_settingNames = list(self.settings.view.__dict__)

    @property
    def difference_heatmaps_path(self):
        cpf = self.settings._paths.cum_plot_file_path
        return cpf.parents[1].joinpath('difference', cpf.parts[-1])

    def test_with_current_settings_then_reset_to_DefaultSettings(
            self, sub_study_name: str, **kwargs):
        aiana = AianaMain(self.settings)
        if self.open_oct_viewer:
            aiana.create_and_view_octfile_for_SceneInspection(**kwargs)
        aiana.settings.sim.sub_study_name = f'testing_{sub_study_name}'
        aiana.settings.update_sim_dt_and_paths()
        if self.run_simulation:
            # clear instantaneous_csv_files:
            folder = aiana.settings._paths.inst_csv_parent_folder
            if folder.exists():
                fi.clear_folder_content(folder)
            aiana.simulate_and_evaluate(tasks=['sim'])  # dont plot all time steps

        if self.mode == 'test':
            try:
                self._load_df_test_and_df_ref()
                aiana.plotterObj.ground_heatmap(
                    self._get_difference_data(),
                    destination_file_path=self.difference_heatmaps_path,
                    cumulative=True)
                self._fill_RMSE_MBE_csv(sub_study_name)
            except Exception:
                raise Exception(
                    'Could not load reference simulation results, try using \
                    mode=create_reference, at first.')
        self.overwrite_settings_by_default_settings()

    # =========================================================================

    def test_inverted_bool_settings(self, bool_setting_names: list, **kwargs):
        """tests the attributes in bool_setting_names list
            one by one with inverted values.

            bool_setting_names list of strings being the names of the bool
            attributes that should be tested with inverted values.
        """
        self.overwrite_settings_by_default_settings()
        for attr_name in bool_setting_names:
            parentObj = self._find_out_attr_parentObj(attr_name)
            currentValue = getattr(parentObj, attr_name)
            assert type(currentValue) == bool,\
                f'{attr_name} is not a bool setting.'
            print(attr_name, 'was set to', currentValue,
                  '-> testing', not currentValue, 'now...')
            setattr(parentObj, attr_name, not currentValue)
            self.test_with_current_settings_then_reset_to_DefaultSettings(
                sub_study_name=f'{attr_name}-{not currentValue}', **kwargs)
        return

    def test_dictItems_separately(
            self, settings_dict_name: str, test_dict: dict, **kwargs):
        """this method tests the passed settings dictionary ("test_dict").
        However not all items at once. Instead, each item is tested in a loop
        seperately by changing the value only within a "temp_dict" with
        otherwise default settings as written in "default_dict".

        Args:
            settings_dict_name (str): name of the dictionary in the settings,
            whichs items will be tested seperately with the values
            written in test_dict.
            test_dict (dict): see settings_dict_name doc string.

            **kwargs: add_groundScanArea: bool = True,
            add_sensor_vis: bool = True,
            add_NorthArrow: bool = True,
            view_name: str = 'total' or 'top_down'
        """
        self.overwrite_settings_by_default_settings()
        for key in test_dict:
            parentObj = self._find_out_attr_parentObj(settings_dict_name)
            # has to be placed within the loop as _test_then_resetSettings()
            # will create a new copy of the settings object and pass it to
            # the simulation while changing the settings of the first copy
            default_dict: dict = getattr(parentObj, settings_dict_name)
            assert type(default_dict) == dict,\
                f'{settings_dict_name} is not a dict.'
            if key not in default_dict:
                raise KeyError(
                    f'{key} not found in {settings_dict_name}. '
                    f'Valid keys are {list(default_dict.keys())}.'
                )
            temp_dict = default_dict.copy()
            temp_dict[key] = test_dict[key]
            setattr(self.settings.apv, settings_dict_name, temp_dict)

            self.test_with_current_settings_then_reset_to_DefaultSettings(
                sub_study_name=f'{key}-{temp_dict[key]}', **kwargs)

    def test_listItems_separately(
            self, setting_name: str, test_list: list, **kwargs):
        """
        applies the test_list items one by one onto the settings-attribute
        having settings_name as name and the types str, int, float or list.
        """
        self.overwrite_settings_by_default_settings()
        for item in test_list:
            parentObj = self._find_out_attr_parentObj(setting_name)
            type_of_setting = type(getattr(parentObj, setting_name))
            assert type_of_setting in [str, int, float, list], (
                f'The type of the tested setting when using this '
                'method test_listItems_separately() was expected '
                f'to be "str, int, float or list", but is {type_of_setting}.'
                f'(setting name: {setting_name}).')
            setattr(parentObj, setting_name, item)
            self.test_with_current_settings_then_reset_to_DefaultSettings(
                sub_study_name=f'{setting_name}-{item}', **kwargs)

    def overwrite_settings_by_default_settings(self):
        self.settings = copy.deepcopy(self.default_settings)
        self.settings.update_sim_dt_and_paths()

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

    # #########################
    # test evaluation

    def _load_df_test_and_df_ref(self):
        csv_path_test = self.settings._paths.cum_csv_file_path
        if not csv_path_test.exists():
            raise Exception(f'No simulation results found for {csv_path_ref}',
                            'run simulation first with run_simulation=True,',
                            'and mode = "test".')

        # go up in path to parent 3 times (starts at 0 and filename counts as
        # well), and join folder name 'reference' and the last to
        # parts (cum csv folder + file) of csv_path_test:
        csv_path_ref = csv_path_test.parents[2].joinpath(
            'reference', *csv_path_test.parts[-2:])

        if not csv_path_ref.exists():
            raise Exception(f'No reference results found for {csv_path_ref}',
                            'run simulation first with run_simulation=True,',
                            'and mode = "create_reference".')

        self.df_test = fi.df_from_file_or_folder(csv_path_test)
        self.df_ref = fi.df_from_file_or_folder(csv_path_ref)

    def _fill_RMSE_MBE_csv(self, sub_study_name):
        z = Plotter.get_label_and_cm_input(
            self.settings.sim.cm_quantity, True)['z']
        statistics = calc_RMSE_MBE(
            self.df_test[z], self.df_ref[z])

        # HEADER: 'sub_study_name-test_date   mbe   rel_mbe   rmse   rel_rmse'
        result_row = f'{sub_study_name}-{datetime.now()}'
        for item in statistics:
            result_row += f'\t{item}'
        result_row += '\n'
        fi.write_to_txt_file(self.RMSE_MBE_csv_path, result_row, mode='a')

    def _get_difference_data(self) -> pd.DataFrame:
        """df result is needed for plotting difference heatmap"""
        df_dif = self.df_ref.copy()  # blueprint reusing indices etc.
        quantities = ['Whm2', 'PARGround_cum', 'ShadowDepth_cum']
        if 'DLI' in df_dif.columns:
            quantities += ['DLI']
        for col in quantities:
            try:
                df_dif.loc[:, col] = self.df_test.loc[:, col]\
                    - self.df_ref.loc[:, col]
            except KeyError:
                raise Exception(f'valid cols: {df_dif.columns}')
        return df_dif
