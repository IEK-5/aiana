from pathlib import Path
import sys
import numpy as np
import pandas as pd
from apv.classes.util_classes.geometries_handler import GeometriesHandler

from apv.classes.util_classes.settings_grouper import Settings
from apv.utils import files_interface as fi
import bifacial_radiance as br
import concurrent.futures
import subprocess
from typing import Iterator
from tqdm.auto import trange


class Simulator:
    ygrid: list[int]
    groundscan: dict
    # frontscan: dict
    # backscan: dict
    df_ground_results: pd.DataFrame

    analObj: br.AnalysisObj

    def __init__(self, settings: Settings, debug_mode=False):
        self.settings = settings
        self.debug_mode = debug_mode

        # instantiate analysis
        self.analObj = br.AnalysisObj(
            octfile=self.settings.names.oct_fn,
            # name=self.radObj.name # TODO needed?
        )
        self.temp_results_folder: Path = \
            self.settings.paths.bifacial_radiance_files / Path('results')
        self._set_scan_dicts_and_ygrid()

    def _set_scan_dicts_and_ygrid(self):
        """
        groundscan (dict): dictionary containing the XYZ-start and
        -increments values for a bifacial_radiance linescan.
        It describes where the virtual ray tracing sensors are placed.
        The origin (x=0, y=0) of the PV facility is in its center.
        """

        ghObj = GeometriesHandler(self.settings.apv, self.debug_mode)

        # number of sensors on ground against y-axis (along x-axis)
        sensorsy = int(ghObj.x_field / self.settings.sim.spatial_resolution)+1

        # TODO not yet tested, sensory will be wrong for tilted module
        
        self.groundscan = {
            'xstart':  ghObj.scan_area_anchor_x,
            'ystart': 0,  # will be set later by looping through ygrid
            'zstart': 0.05,
            'xinc': self.settings.sim.spatial_resolution, 'yinc': 0,
            'zinc': 0, 'Nx': 1, 'Ny': sensorsy, 'Nz': 1,
            'orient': '1 0 0'  # see br.main() line ~3867 for tilt = 0:
            # ground similar to frontscan: -cos(0) -sin(0) -sin(0) = -1 0 0
        }
        self.ygrid: list[float] = np.arange(
            ghObj.scan_area_anchor_y,
            (ghObj.scan_area_anchor_y + ghObj.y_field
             + self.settings.sim.spatial_resolution),
            self.settings.sim.spatial_resolution)

        print(f'\n sensor grid:\nx: {sensorsy}, y: {len(self.ygrid)}, '
              f'total: {sensorsy * len(self.ygrid)}')

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
                    self._run_line_scan, self.ygrid
                )
                for result in results:
                    print(result)
        else:
            # trange for status bar
            for i in trange(len(self.ygrid)):
                self._run_line_scan(self.ygrid[i])

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
            """
            self.frontscan['ystart'] = y_start
            self.backscan['ystart'] = y_start

            self.analObj.analysis(self.settings.names.oct_fn,
                        temp_name,
                        self.frontscan,
                        self.backscan,
                        accuracy=self.settings.sim.ray_tracing_accuracy)
            """
        elif self.settings.sim.scan_target == 'ground':
            self.groundscan['ystart'] = y_start

            self.analObj.analysis(
                self.settings.names.oct_fn,
                temp_name,
                self.groundscan,
                accuracy=self.settings.sim.ray_tracing_accuracy
            )

            """linepts = self.analObj._linePtsMakeDict(self.groundscan)
            groundDict = self.analObj._irrPlot(
                self.settings.names.oct_fn, linepts, temp_name+'_Ground',
                # plotflag=True can be tested
                accuracy=self.settings.sim.ray_tracing_accuracy
            )
            self.analObj._saveResults(
                groundDict, savefile=f'irr_{temp_name}.csv'
            )"""

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
        print(f'merged file saved in {self.settings.paths.csv_file_path}\n')
        self.df_ground_results = df
