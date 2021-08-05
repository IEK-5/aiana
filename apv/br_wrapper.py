# #
''' Called by main.py with the needed parameters to set the neccessary
objects, create scene and run simulation with Bifacial_Radiance according
to presets in settings.py
'''
# import needed packages
import subprocess
# from pvlib import *
import numpy as np
import pandas as pd
import datetime as dt
import time
import json
import os
import pytictoc
from pathlib import Path
from tqdm.auto import trange
import concurrent.futures
import bifacial_radiance as br

import apv
from apv.settings import UserPaths
from apv.utils import files_interface as fi

# #


class BifacialRadianceObj:
    # TODO clean up prints (especially data frames)
    """
    Attributes:
        simSettings (apv.settings.Simulation): simulation settings object
        --------
        radObj (bifacial_radiance.RadianceObj): radiance object
        scene (bifacial_radiance.SceneObj): scene object
        oct_file_name (str): .oct file name with or without extension
        met_data(bifacial_radiance.MetObj): meterologic data object

        the ones above are retrieved from running setup_br()
        --------
        x_field (int): lengths of the groundscan area in x direction
        according to scene + 2 m each side
        y_field (int): lengths of the groundscan area in y direction

        the ones above are calculated automatically on initialisation
        but can also be set manually
        ---> fehlt noch, besser auch grupieren in ein objekt.
    """

    def __init__(
            self,
            simSettings=apv.settings.Simulation(),
            weather_file=None,
            # create_oct_file=True
    ):
        self.simSettings: apv.settings.Simulation = simSettings
        self.weather_file = weather_file
        # self.create_oct_file = create_oct_file

        self.radObj: br.RadianceObj = None
        self.scene: br.SceneObj = None
        self.oct_file_name: str = None
        self.met_data: br.MetObj = None
        self.analObj: br.AnalysisObj = None

        self.x_field: int = 0
        self.y_field: int = 0
        self.ygrid: list[int] = []
        self.groundscan = dict()

        self.df_ground_results = pd.DataFrame()
        self.csv_file_name = str()

        self.setup_br()

    def setup_br(self):
        """
        veraltet

        Creates the scene according to parameters and presets defined in
        settings.py - scene created as follows:
        0- adjust settings
        1- create Radiance-Object
        2- setting albedo of ground
        3- read TMY data (from EPW or pre-installed)
        4- create module (either cell defined or not)
        5- create structure object
        6- create sky according to modelling model 'gendaylit' or 'gencumsky'
        7- define number of panels, rows, and columns and final scene (.oct)

        Args:
            sim_type (str, optional): 'gendaylit' for perez hourly analysis
            or 'gencumsky' for cumulative perez model

            cellLevelModule (bool, optional):
            assign module acccording to cell level parameters if true.

            EPW (bool, optional):
            True: downloads nearest EPW data
            False: checks downloaded TMY data.

        Returns:
            radObj: Radiance Object
            scene:
            metdata: Meteorological csv data
        """

        self.simSettings = apv.utils.settings_adjuster.adjust_settings(
            self.simSettings)

        working_folder = UserPaths.bifacial_radiance_files_folder
        # check working folder
        fi.make_dirs_if_not_there(working_folder)

        # create Bifacial_Radiance Object with ground
        self.radObj = br.RadianceObj(
            self.simSettings.sim_name, path=str(working_folder))
        self.radObj.setGround(self.simSettings.ground_albedo)

        # read TMY or EPW data
        if self.weather_file is None:
            self.weather_file = self.radObj.getEPW(
                lat=self.simSettings.apv_location.latitude,
                lon=self.simSettings.apv_location.longitude)

        self.met_data = self.radObj.readWeatherFile(
            weatherFile=str(self.weather_file))

        # create PV module
        # default for standard:
        rad_text = None
        cellLevelModuleParams = None

        if self.simSettings.module_form == 'cell_level':
            cellLevelModuleParams = self.simSettings.cellLevelModuleParams

        if self.simSettings.module_form == 'cell_level_checker_board':
            rad_text = apv.utils.radiance_geometries.checked_module(
                self.simSettings
            )

        if self.simSettings.module_form == 'EW_fixed':
            rad_text = apv.utils.radiance_geometries.make_text_EW(
                self.simSettings
            )

        self.radObj.makeModule(
            name=self.simSettings.module_name,
            **self.simSettings.moduleDict,
            cellLevelModuleParams=cellLevelModuleParams,
            text=rad_text
        )

        # create structure <To BE DEFINED LATER>

        # Create Sky
        # gendaylit using Perez models for direct and diffuse components
        if self.simSettings.sky_gen_mode == 'gendaylit':
            timeindex = apv.utils.time.get_hour_of_year(
                self.simSettings.sim_date_time)
            # if (self.simSettings.start_time == '') and (
            # self.simSettings.end_time == ''):
            self.radObj.gendaylit(timeindex=timeindex)
            self.oct_file_name = self.radObj.name \
                + '_' + self.simSettings.sim_date_time
            self.scene = self.radObj.makeScene(
                moduletype=self.simSettings.module_name,
                sceneDict=self.simSettings.sceneDict
            )
            self.radObj.makeOct(  # self.radObj.getfilelist(), #passiert autom.
                octname=self.oct_file_name)

        # gencumskyself.met_data
        if self.simSettings.sky_gen_mode == 'gencumsky':
            self.radObj.genCumSky(epwfile=self.weather_file,
                                  startdt=self.simSettings.startdt,
                                  enddt=self.simSettings.enddt)

            self.oct_file_name = self.radObj.name \
                + '_' + 'Cumulative'

            self.scene = self.radObj.makeScene(
                moduletype=self.simSettings.module_name,
                sceneDict=self.simSettings.sceneDict)

            self.radObj.makeOct(self.radObj.getfilelist(),
                                octname=self.oct_file_name)

        '''
            else:
                begin = int(self.simSettings.start_time)
                end = int(self.simSettings.end_time) + 1
                for timeindex in np.arange(begin, end, 1):
                    dni = self.met_data.dni[timeindex]
                    dhi = self.met_data.dhi[timeindex]
                    # solar position
                    solpos = self.met_data.solpos.iloc[timeindex]
                    sunalt = float(solpos.elevation)
                    sunaz = float(solpos.azimuth)
                    print(timeindex)
                    self.oct_file_name = self.radObj.name \
                        + '_{}'.format(timeindex)
                    sky = self.radObj.gendaylit2manual(dni, dhi, sunalt, sunaz)
                    self.radObj.makeOct(octname=self.oct_file_name)
                '''
        # placed here to allow for access also without a simulation run
        self.csv_file_name = self.oct_file_name + '.csv'

        # calculate ground grid parameters
        sceneDict = self.simSettings.sceneDict
        moduleDict = self.simSettings.moduleDict
        cellLevelModuleParams = self.simSettings.cellLevelModuleParams
        if self.simSettings.module_form == 'cell_level_checker_board':
            self.x_field = cellLevelModuleParams['xcell']*4
            self.y_field = cellLevelModuleParams['ycell']*4

        else:
            self.x_field: int = round(
                sceneDict['nMods'] * moduleDict['x']) + 2*4

            self.y_field: int = round(
                sceneDict['pitch'] * sceneDict['nRows']
                + moduleDict['y'] * moduleDict['numpanels']) + 2*2

        self.ygrid: list[float] = np.arange(
            -self.y_field / 2,
            (self.y_field / 2) + 1,
            self.simSettings.spatial_resolution)

        self._set_up_AnalObj_and_groundscan()

    def view_scene(self, view_name: str = 'total', oct_file_name=None):
        """views an .oct file via radiance/bin/rvu.exe

        Args:
            view_name (str): select from ['total', ...]
            as defined in settingself.simSettings.scene_camera_dicts
            a .vp file will be stored with this name in
            e.g. 'C:\\Users\\Username\\agri-PV\\views\\total.vp'

            oct_fn (str): file name of the .oct file without extension
            being located in the view_fp parent directory (e.g. 'Demo1')
            Defaults to settings.Simulation.name.
        """

        if oct_file_name is None:
            oct_file_name = self.oct_file_name

        scd = self.simSettings.scene_camera_dicts[view_name]

        for key in scd:
            scd[key] = str(scd[key]) + ' '

        view_fp = UserPaths.bifacial_radiance_files_folder / Path(
            'views/'+view_name+'.vp')

        with open(view_fp, 'w') as f:
            f.write(
                'rvu -vtv -vp '
                + scd['cam_pos_x']
                + scd['cam_pos_y']
                + scd['cam_pos_z']
                + '-vd '
                + scd['view_direction_x']
                + scd['view_direction_y']
                + scd['view_direction_z']
                + '-vu 0 0 1 '
                + '-vh '
                + scd['horizontal_view_angle']
                + '- vv '
                + scd['vertical_view_angle']
                + '-vs 0 -vl 0'
            )

        subprocess.call(
            ['rvu', '-vf', view_fp, '-e', '.01', oct_file_name+'.oct'])

    def _set_up_AnalObj_and_groundscan(self):

        octfile = self.oct_file_name

        # add extension if not there:
        if octfile[-4] != '.oct':
            octfile += '.oct'

        # instantiate analysis
        self.analObj = br.AnalysisObj(
            octfile=octfile, name=self.radObj.name)

        # number of sensors on ground against y-axis (along x-axis)
        sensorsy = np.round(self.x_field / self.simSettings.spatial_resolution)
        if (sensorsy % 2) == 0:
            sensorsy += 1

        print(f'\n sensor grid:\nx: {sensorsy}, y: {len(self.ygrid)}, '
              f'total: {sensorsy * len(self.ygrid)}')

        # start rough scan to define ground afterwards
        groundscan, backscan = self.analObj.moduleAnalysis(scene=self.scene,
                                                           sensorsy=sensorsy)

        self.groundscan = self._set_groundscan(groundscan)

    def _set_groundscan(self, groundscan: dict) -> dict:
        """Modifies the groundscan dictionary, except for 'ystart',
        which is set later by looping through ygrid.

        Args:
            groundscan (dict): dictionary containing the XYZ-start and
            -increments values for a bifacial_radiance linescan.
            It describes where the virtual ray tracing sensors are placed.
            The origin (x=0, y=0) of the PV facility is in its center.

        Returns:
            groundscan (dict)
        """
        groundscan['xstart'] = - self.x_field / 2
        groundscan['xinc'] = self.simSettings.spatial_resolution
        groundscan['zstart'] = 0.05
        groundscan['zinc'] = 0
        groundscan['yinc'] = 0

        return groundscan

    def run_line_scan(self, y_start):
        groundscan_copy = self.groundscan.copy()
        groundscan_copy['ystart'] = y_start
        temp_name = self.radObj.name + "_groundscan" \
            + '{:.3f}'.format(y_start)

        backscan = groundscan_copy
        self.analObj.analysis(self.oct_file_name+'.oct',
                              temp_name,
                              groundscan_copy,
                              backscan,
                              accuracy=self.simSettings.ray_tracing_accuracy,
                              only_ground=self.simSettings.only_ground_scan)

        # TODO TypeError: can only concatenate tuple (not "int") to tuple
        # sim_progress =100*(np.where(self.ygrid == y_start)+1)/len(self.ygrid)
        # return f'Sim progress {sim_progress} %.'
        return f'y_start: {y_start} done.'

    def run_raytracing_simulation(self) -> pd.DataFrame:
        """provides irradiation readings on ground in form of a Dataframe
        as per predefined resolution.
        """

        # clear temporary line scan results from bifacial_results_folder
        temp_results: Path = UserPaths.bifacial_radiance_files_folder / Path(
            'results')
        fi.clear_folder_content(temp_results)

        # to measure elapsed time:
        tictoc = pytictoc.TicToc()
        tictoc.tic()

        if self.simSettings.use_multi_processing:

            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = executor.map(self.run_line_scan, self.ygrid)

                for result in results:
                    print(result)
        else:
            # trange for status bar
            for i in trange(len(self.ygrid)):
                self.run_line_scan(self.ygrid[i])

        tictoc.toc()
        print('\n')

        self.merge_line_scans()
        return

    def merge_line_scans(self):
        """merge results to create one complete ground DataFrame
        """
        temp_results: Path = UserPaths.bifacial_radiance_files_folder / Path(
            'results')
        df_ground_results: pd.DataFrame = fi.df_from_file_or_folder(
            temp_results, append_all_in_folder=True)

        df_ground_results = df_ground_results.reset_index()

        if self.simSettings.only_ground_scan:
            col_name = 'Wm2'
        else:
            col_name = 'Wm2Front'
        df_ground_results = df_ground_results.rename(
            columns={col_name: 'Wm2Ground'})
        # Path for saving final results
        fi.make_dirs_if_not_there(UserPaths.results_folder)
        f_result_path = os.path.join(UserPaths.results_folder,
                                     self.csv_file_name)
        df_ground_results.to_csv(f_result_path)
        print(f'merged file saved in {f_result_path}\n')
        self.df_ground_results = df_ground_results
        return

    def plot_ground_insolation(self, df=None):
        """plots the ground insolation as a heat map and saves it into
            the results/plots folder.

        Args:
            df (pd.DataFrame): if None, a df is created
            from the csv file name stored in an instance of this class.
            Defaults to None.
        """

        if df is None:
            df = apv.utils.files_interface.df_from_file_or_folder(
                apv.settings.UserPaths.results_folder / Path(
                    self.csv_file_name))

        ticklabels_skip_count_number = int(
            2/self.simSettings.spatial_resolution)
        if ticklabels_skip_count_number < 2:
            ticklabels_skip_count_number = "auto"

        fig = apv.utils.plots.plot_heatmap(
            df, 'y', 'x', 'Wm2Ground',
            x_label='x [m]', y_label='y [m]',
            z_label='ground irradiance [W m$^{-2}$]',
            ticklabels_skip_count_number=ticklabels_skip_count_number
        )

        apv.utils.files_interface.save_fig(fig, self.oct_file_name)

# #
