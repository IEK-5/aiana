from pathlib import Path
from apv.settings.apv_system_settings import Default as SystSettings
from apv.settings.view_settings import ViewSettings
from apv.settings.sim_settings import Simulation
from apv.settings.user_paths import UserPaths


class Settings:
    def __init__(self):
        self.apv = SystSettings()
        self.view = ViewSettings()
        self.sim = Simulation()
        self.set_names_and_paths()
        self._verify_unique_setting_names()

    def set_names_and_paths(self):
        self.names = Names(self.sim, self.apv)
        self.paths = Paths(self.sim, self.names)

    # #
    def _verify_unique_setting_names(self):
        all_settings_names = list(self.sim.__dict__)\
            + list(self.apv.__dict__) + list(self.view.__dict__)
        for name in all_settings_names:
            if all_settings_names.count(name) > 1:
                raise Exception(f'Duplicate setting name found: {name}')
    # TODO https://stackoverflow.com/questions/9522877/pythonic-way-to-have-a-choice-of-2-3-options-as-an-argument-to-a-function
    # to assert the Literals (e.g. module_form) see link above. Variables
    # need to be splitted in type and value, only then allowed string list can
    # be accessed by Literal.get_args(). Options would need to be shown in comments then
    # which is meaningful as the usershould not change the options and only
    # pick one of them...


class Names:
    # Radiance scene file name (.oct) and the output files
    oct_fn: str
    csv_fn_ext: str  # fn_ext = file name extension added behind ground_results

    def __init__(self, SimSettings: Simulation,
                 APV_SystSettings: SystSettings):

        self.csv_fn_ext = SimSettings.sim_date_time.replace(':', 'h')+'.csv'

        self.oct_fn = SimSettings.study_name \
            + '_' + APV_SystSettings.module_form \
            + '.oct'
        # + '_' + self.csv_fn.replace('.csv', '.oct')#
        # ^-- this was commented out because an oct file can be >80 mb
        # and thus its waste of disc space to store e.g. each time step


class Paths(UserPaths):
    def __init__(self, SimSettings: Simulation, FileNames: Names):
        # file paths of oct file without and with sky
        self.oct_fp_noSky = self.bifacial_radiance_files / Path(
            FileNames.oct_fn[:-4]+'_withoutSky.oct')
        self.oct_fp = self.bifacial_radiance_files / Path(
            f'{FileNames.oct_fn}')

        # file paths for saving results
        self.results_folder: Path = self.results_parent_folder \
            / SimSettings.results_subfolder
        self.csv_parent_folder: Path = self.results_folder / 'data'
        self.csv_file_path: Path = self.csv_parent_folder /\
            f'ground_results_{FileNames.csv_fn_ext}'

        # NOTE check folder existence is done right before saving sim results
        # to avoid creating empty folders upon init
