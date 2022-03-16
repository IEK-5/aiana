import sys
import pandas as pd
from pathlib import Path
import concurrent.futures
from typing import Iterator
from tqdm.auto import trange
import bifacial_radiance as br

from apv.utils import files_interface as fi
from apv.classes.util_classes.settings_grouper import Settings
from apv.classes.util_classes.geometries_handler import GeometriesHandler


class Simulator:
    df_ground_results: pd.DataFrame
    ghObj: GeometriesHandler  # needed for scan points
    analObj: br.AnalysisObj

    def __init__(
        self, settings: Settings, ghObj: GeometriesHandler,
        debug_mode=False
    ):
        self.settings = settings
        self.debug_mode = debug_mode

        # instantiate analysis
        self.analObj = br.AnalysisObj(
            octfile=self.settings.names.oct_fn,
            # name=self.radObj.name # TODO needed?
        )
        self.ghObj = ghObj

        self.temp_results_folder: Path = \
            self.settings.paths.bifacial_radiance_files / Path('results')

    def run_raytracing_simulation(
            self, skip_if_result_exists=True) -> pd.DataFrame:
        """provides irradiation readings on ground in form of a Dataframe
        as per predefined resolution.
        """
        csv_file_path = self.settings.paths.csv_file_path
        if csv_file_path.exists() and not skip_if_result_exists:
            print(f'\nSimulation result {csv_file_path} already there.\n')
            return

        # clear temporary line scan results from bifacial_results_folder
        fi.clear_folder_content(self.temp_results_folder)

        if self.settings.sim.use_multi_processing:

            with concurrent.futures.ProcessPoolExecutor() as executor:
                results: Iterator = executor.map(
                    self._run_line_scan, self.ghObj.ygrid
                )
                for result in results:
                    print(result)
        else:
            # trange for status bar
            for i in trange(len(self.ghObj.ygrid)):
                self._run_line_scan(self.ghObj.ygrid[i])

        print('\n')

        self.merge_line_scans()

    def _run_line_scan(self, y_start):

        temp_name = (
            f'{self.settings.sim.study_name}_{self.settings.sim.scan_target}_'
            f'scan_{y_start:.3f}'
        )
        if self.settings.sim.scan_target == 'module':
            sys.exit("scan_target = 'module' is not yet supported"
                     "but prepared in code...")

            self.frontscan, self.backscan = self.analObj.moduleAnalysis(
                scene=self.scene, sensorsy=self.ghObj.sensors_x)
            # sensory = sensors along module-width (which is along x)

            self.frontscan['ystart'] = y_start
            self.backscan['ystart'] = y_start

            self.analObj.analysis(
                self.settings.names.oct_fn, temp_name,
                self.frontscan, self.backscan,
                accuracy=self.settings.sim.ray_tracing_accuracy)

        elif self.settings.sim.scan_target == 'ground':
            self.ghObj.groundscan['ystart'] = y_start
            linepts = self.analObj._linePtsMakeDict(
                self.ghObj.groundscan)
            print('\nLinepoints: ', linepts)
            groundDict = self.analObj._irrPlot(
                self.settings.names.oct_fn, linepts, temp_name+'_Ground',
                # plotflag=True can be tested
                accuracy=self.settings.sim.ray_tracing_accuracy
            )
            self.analObj._saveResults(
                groundDict, savefile=f'irr_{temp_name}.csv'
            )
        return f'y_start: {y_start} done.'

    def merge_line_scans(self):
        """merge results to create one complete ground DataFrame
        """
        df: pd.DataFrame = fi.df_from_file_or_folder(
            self.temp_results_folder, append_all_in_folder=True,
            print_reading_messages=False)
        df = df.reset_index()

        fi.make_dirs_if_not_there(self.settings.paths.csv_parent_folder)
        # #NOTE done here to avoid creating empty folders,
        # if csv parent folder is changed from outside)

        df.to_csv(self.settings.paths.csv_file_path)
        print(f'merged line scans into {self.settings.paths.csv_file_path}\n')
        self.df_ground_results = df
