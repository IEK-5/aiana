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

import sys
import pandas as pd
from pathlib import Path
import concurrent.futures
from typing import Iterator, Literal, Tuple
from tqdm.auto import trange
import bifacial_radiance as br
from subprocess import Popen, PIPE  # replacement for os.system()

from aiana.utils import files_interface as fi
from aiana.classes.util_classes.settings_handler import Settings
from aiana.classes.rad_txt_related.geometries_handler import GeometriesHandler
from aiana.classes.util_classes.print_hider import PrintHider


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
            octfile=self.settings._names.oct_fn,
            # name=self.radObj.name # TODO needed?
        )
        self.ghObj = ghObj

        self.temp_results_folder: Path = \
            self.settings._paths.radiance_input_files / Path('results')

    def run_raytracing_simulation(self, skip_if_result_exists=True):
        """provides irradiation readings on ground in form of a Dataframe
        as per predefined resolution.
        """
        # eventually create results (parent) folder existence
        fi.make_dirs_if_not_there(self.settings._paths.inst_csv_parent_folder)
        # #NOTE done here to avoid creating empty folders,
        # if csv parent folder is changed from outside)

        # check for results file
        csv_file_path = self.settings._paths.inst_csv_file_path
        if csv_file_path.exists() and not skip_if_result_exists:
            print(f'\nSimulation result {csv_file_path} already there.\n')
            return
        # clear temporary line scan results from bifacial_results_folder
        fi.clear_folder_content(
            self.temp_results_folder, print_msg=False)
        if self.settings.sim.use_accelerad_GPU_processing:
            self._run_area_scan(self.ghObj.ground_areaScan)
            if self.settings.sim.use_CPU_multi_processing:
                print('GPU and CPU multiprocessing were both set to True.',
                      'GPU has priority, CPU multiprocessing is not used.')

        elif self.settings.sim.use_CPU_multi_processing:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results: Iterator = executor.map(
                    self._run_line_scan, self.ghObj.ygrid
                )
                for result in results:
                    print(result)
            self.merge_line_scans()

        else:
            # trange for status bar
            for i in trange(len(self.ghObj.ygrid)):
                self._run_line_scan(self.ghObj.ygrid[i])
            self.merge_line_scans()

    def _run_area_scan(self, scanDict: dict):
        """with gpu -> simulate all scan lines at once"""
        linepts = self._write_linepts(scanDict)
        for i in range(4):
            try:
                with PrintHider():  # otherwise accelerad prints a lot...
                    # this will run the actual simulation:
                    groundDict = self._irrPlotMod_modified(
                        self.settings._names.oct_fn, linepts)
                    self.analObj._saveResults(
                        groundDict,
                        savefile=self.settings._paths.inst_csv_file_path
                    )
                    break
            except TypeError:  # 'NoneType' object is not subscriptable
                # rarely there is a accelerad polygon problem, e.g.:
                # accelerad_rtrace: fatal - (!xform...:
                # bad arguments for polygon "a4.1.a1.SUNFARMING.6457"
                # in this case data will be empty (NoneType).
                if i < 3:
                    print('TypeError: result data empty, trying again...')
                else:
                    print('Simulator._run_area_scan() returned NoneType 4x,',
                          'something wrong with the oct-file or linepts?',
                          'You can also try self._irrPlotMod_modified()',
                          'without PrintHider.')

        if self.debug_mode:
            print('Area scan done.')

    def _run_line_scan(self, y_start):

        temp_name = (
            f'_{self.settings.sim.scan_target}_'
            f'scan_{y_start:.3f}'
        )
        if self.settings.sim.scan_target == 'module':
            raise Exception("scan_target = 'module' is not yet supported"
                            "but prepared in code...")

            self.frontscan, self.backscan = self.analObj.moduleAnalysis(
                scene=self.scene, sensorsy=self.ghObj.n_sensors_x)
            # sensory = sensors along module-width (which is along x)

            self.frontscan['ystart'] = y_start
            self.backscan['ystart'] = y_start

            self.analObj.analysis(
                self.settings._names.oct_fn, temp_name,
                self.frontscan, self.backscan,
                accuracy=self.settings.sim.ray_tracing_accuracy)

        elif self.settings.sim.scan_target == 'ground':
            self.ghObj.ground_lineScan['ystart'] = y_start
            linepts = self._write_linepts(self.ghObj.ground_lineScan)
            groundDict = self._irrPlotMod_modified(
                self.settings._names.oct_fn, linepts)
            self.analObj._saveResults(
                groundDict, savefile=f'irr_{temp_name}.csv'
            )
        print(f'y_start: {y_start} done.')

    # #
    def _write_linepts(self, scanDict: dict) -> str:
        """creates a tape of sensor coordinates within a plane, as defined in
        the scanDict, which is used by BR as input when calling rtrace"""
        d = scanDict
        linepts = ""
        for iz in range(int(d['Nz'])):
            for ix in range(int(d['Nx'])):
                for iy in range(int(d['Ny'])):
                    xpos = d['xstart'] + ix*d['xinc']
                    ypos = d['ystart'] + iy*d['yinc']
                    zpos = d['zstart'] + iz*d['zinc']
                    linepts += f'{xpos} {ypos} {zpos} {d["orient"]} \r'
        return linepts

    def merge_line_scans(self):
        """merge results to create one complete ground DataFrame
        """
        df: pd.DataFrame = fi.df_from_file_or_folder(
            self.temp_results_folder, append_all_in_folder=True,
            print_reading_messages=False)
        df = df.reset_index()

        df.to_csv(self.settings._paths.inst_csv_file_path)
        print(f'merged line scans into {self.settings._paths.inst_csv_file_path}\n')
        self.df_ground_results = df

    def _irrPlotMod_modified(self, octfile, linepts) -> dict[str, list]:
        """
        Copyright (c) 2017-2021, Alliance for Sustainable Energy, LLC
        All rights reserved. (see BSD 3-Clause License)

        Copied and modified from bifacial_radiance.main.py to be able
        to switch between CPU and GPU parallelization and to change radiance
        settings
        ------------
        octfile : string
            Filename and extension of .oct file
        linepts :
            Output from :py:class:`simulator._write_linepts()`

        Returns
        -------
        out : dictionary
            out.x,y,z  - coordinates of point
            .r,g,b     - r,g,b values in Wm-2
            .Wm2            - equal-weight irradiance
            .mattype        - material intersected
            .title      - title passed in
        """

        assert octfile is not None, 'Analysis aborted. octfile == None'

        keys = ['Wm2', 'x', 'y', 'z', 'r', 'g', 'b', 'mattype']
        out = {key: [] for key in keys}
        # out = dict.fromkeys(['Wm2','x','y','z','r','g','b','mattype','title'])

        if self.settings.sim.use_accelerad_GPU_processing:
            prefix = 'accelerad_'
        else:
            prefix = ''

        s = self.settings.sim.rtraceAccuracyDict[
            self.settings.sim.rtraceAccuracy]
        for key in s:
            s[key] = str(s[key])
        cmd = (f"{prefix}rtrace -i -ab {s['ab']} -aa {s['aa']} -ar {s['ar']}"
               f" -ad {s['ad']} -as {s['as']} -h -oovs {octfile}")

        temp_out, err = _popen(cmd, linepts.encode())
        if err is not None:
            if err[0: 5] == 'error':
                raise Exception(err[7:])
            else:
                print(err)

        # when file errors occur, temp_out is None, and err message is printed.
        if temp_out is not None:
            for line in temp_out.splitlines():
                temp = line.split('\t')
                out['x'].append(float(temp[0]))
                out['y'].append(float(temp[1]))
                out['z'].append(float(temp[2]))
                out['r'].append(float(temp[3]))
                out['g'].append(float(temp[4]))
                out['b'].append(float(temp[5]))
                out['mattype'].append(temp[6])
                out['Wm2'].append(sum([float(i) for i in temp[3:6]])/3.0)

        else:
            out = None   # return empty if error message.

        return(out)


def _popen(cmd, data_in, data_out=PIPE):
    """
    Copyright (c) 2017-2021, Alliance for Sustainable Energy, LLC
    All rights reserved. (see BSD 3-Clause License)

    copied also from bifacial_radiance.main.py

    Helper function subprocess.popen replaces os.system
    - gives better input/output process control
    usage: pass <data_in> to process <cmd> and return results
    based on rgbeimage.py (Thomas Bleicher 2010)
    """
    if type(cmd) == str:
        cmd = str(cmd)  # gets rid of unicode oddities
        shell = True
    else:
        shell = False

    # shell=True required for Linux? quick fix, but may be security concern
    p = Popen(cmd, bufsize=-1, stdin=PIPE, stdout=data_out, stderr=PIPE, shell=shell)
    data, err = p.communicate(data_in)
    # if err:
    #    return 'message: '+err.strip()
    # if data:
    #    return data. in Python3 this is returned as `bytes` and needs to be decoded
    if err:
        if data:
            returntuple = (data.decode('latin1'), 'message: '+err.decode('latin1').strip())
        else:
            returntuple = (None, 'message: '+err.decode('latin1').strip())
    else:
        if data:
            returntuple = (data.decode('latin1'), None)  # Py3 requires decoding
        else:
            returntuple = (None, None)

    return returntuple
