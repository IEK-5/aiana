from apv.settings.apv_systems import Default as APV_System
from pathlib import Path
from apv.settings.apv_systems import Default as SystSettings
from apv.settings.view_settings import ViewSettings
from apv.settings.sim_settings import Simulation
from apv.settings.user_paths import UserPaths


class Settings:
    def __init__(self):
        self.apv = SystSettings()
        self.view = ViewSettings()
        self.sim = Simulation()
        self.set_names_and_paths()

    def set_names_and_paths(self):
        self.names = Names(self.sim, self.apv)
        self.paths = Paths(self.sim, self.names)


class Names:
    # Radiance scene file name (.oct) and the output files
    oct_fn: str
    csv_fn: str  # fn = file name

    def __init__(self, SimSettings: Simulation,
                 APV_SystSettings: APV_System):

        self.csv_fn = SimSettings.sim_date_time.replace(':', 'h')+'.csv'

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
            f'ground_results_{FileNames.csv_fn}'

        # NOTE check folder existence is done right before saving sim results
        # to avoid creating empty folders upon init
