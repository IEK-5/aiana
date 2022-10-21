from pathlib import Path
from apv.settings.apv_system_settings import Default as SystSettings
from apv.settings.view_settings import ViewSettings
from apv.settings.sim_settings import Simulation
from apv.settings.user_paths import UserPaths
from apv.classes.util_classes.sim_datetime import SimDT


class Settings:
    """Changing _names, _paths, or _dt from outside is useless, as they will be
    overwritten by applying apv, sim, view, and dt settings.
    To change time, dont use _dt, use the update_sim_dt() method instead"""

    def __init__(self):
        self.apv = SystSettings()
        self.view = ViewSettings()
        self.sim = Simulation()

        self.update_sim_dt_and_paths()
        self._verify_unique_setting_names()

    def update_sim_dt_and_paths(self, **kwargs):
        """**kwargs:
        year: int = ..., month: int = ..., day: int = ...,
        hour: int = ..., minute: int = ..., as in datetime.replace()
        """
        self._dt = SimDT(self.sim)
        self._dt.update_sim_dt(**kwargs)
        self._names = Names(self.sim, self.apv, self._dt)
        self._paths = Paths(self.sim, self._names)

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
    """ Radiance scene file name (.oct) and strings for
    output file names and paths
    """

    def __init__(self, SimSettings: Simulation,
                 APV_SystSettings: SystSettings,
                 dt: SimDT):

        # for inst-plots and -data subfolder-name and cum-file-name:
        self.studyName_modForm_yearMonthDay: str = SimSettings.sub_study_name \
            + f'_{APV_SystSettings.module_form}-module_{dt.sim_dt_str.split(" ")[0]}'

        # for inst plots and data files
        self.dateTimeForFileNames = dt.sim_dt_str.replace(':', 'h')

        self.oct_fn = APV_SystSettings.mountingStructureType \
            + '_' + APV_SystSettings.module_form \
            + '.oct'
        # + '_' + self.csv_fn.replace('.csv', '.oct')#
        # ^-- this was commented out because an oct file can be >80 mb
        # and thus its waste of disc space to store e.g. each time step


class Paths(UserPaths):
    def __init__(self, SimSettings: Simulation, names: Names):
        # file paths of oct file without and with sky
        self.oct_fp_noSky = self.radiance_input_files / Path(
            names.oct_fn[:-4]+'_withoutSky.oct')
        self.oct_fp = self.radiance_input_files / Path(
            f'{names.oct_fn}')

        # file paths for saving results
        self.results_folder: Path = self.results_parent_folder \
            / SimSettings.study_sub_folderName
        self.results_data_folder: Path = self.results_folder \
            / f'{names.studyName_modForm_yearMonthDay}_data'

        self.inst_csv_parent_folder: Path = self.results_data_folder \
            / 'instantaneous_csv_files'  # also used by simulator and evaluator
        self.inst_csv_file_path: Path = self.inst_csv_parent_folder /\
            f'{names.dateTimeForFileNames}.csv'
        self.cum_csv_file_path: Path = self.results_data_folder /\
            f'{names.dateTimeForFileNames}_cumulated.csv'
        # TODO time should be removed in cumulated name

        self.inst_plot_file_path: Path = self.results_data_folder /\
            f'{names.dateTimeForFileNames}_{SimSettings.cm_quantity}.jpg'
        self.cum_plot_file_path: Path = self.results_folder /\
            f'{names.studyName_modForm_yearMonthDay}_{SimSettings.cm_quantity}.jpg'

        # NOTE check folder existence is done right before saving sim results
        # to avoid creating empty folders upon init
