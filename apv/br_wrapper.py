''' Called by main.py with the needed parameters to set the neccessary
objects, create scene and run simulation with Bifacial_Radiance according
to presets in settings.py
'''
# import needed packages
import subprocess
# from pvlib import *
import numpy as np
import pandas as pd
import json
import os
import pytictoc
from pathlib import Path

import bifacial_radiance as br

import apv
from apv.settings import UserPaths
from apv.settings import Simulation as s
from apv.utils import files_interface as fi

# read simulation settings
moduleDict = s.geometries.moduleDict
sceneDict = s.geometries.sceneDict


class BifacialRadianceObj:
    """
    Attributes:

        radObj (bifacial_radiance.RadianceObj):
        radiance Object, retrieved from running setup_br().

        scene (bifacial_radiance.SceneObj):

        oct_fn (str): .oct file name with or without extension

        x_field (int): lengths of the groundscan area in x direction
        according to scene + 2 m each side
        y_field (int): lengths of the groundscan area in y direction
    """

    def __init__(
            self,
            sky_gen_type='gendaylit',
            sim_date_time=s.sim_date_time,
            cellLevelModule=False,
            download_EPW=True
    ):
        self.sky_gen_type = sky_gen_type
        self.cellLevelModule = cellLevelModule
        self.download_EPW = download_EPW
        self.sim_date_time = sim_date_time

        self.radObj: br.RadianceObj = None
        self.scene: br.SceneObj = None
        self.oct_file_name: str = None
        self.met_data: br.MetObj = None
        self.setup_br()

        self.moduleDict: dict[str, float] = s.geometries.moduleDict
        self.sceneDict: dict[str, float] = s.geometries.sceneDict

        self.x_field: int = 0
        self.y_field: int = 0
        self.ygrid: list[int] = []
        self._calc_ground_grid_parameters()

        self.df_ground_results = pd.DataFrame()
        self.csv_file_name = str()

    # read simulation settings

    def setup_br(self):
        """
        veraltet

        Creates the scene according to parameters and presets defined in
        settings.py - scene created as follows:
        1- create Radiance-Object
        2- setting albedo of ground
        3- read TMY data (from EPW or pre-installed)
        4- create module (either cell defined or not)
        5- create structure object
        5- define number of panels, rows, and columns and final scene (.oct)

        Args:
            sim_type (str, optional): 'gendaylit' for hourly analysis
            or 'gencumsky' for annual perez model --> wird perez model
            nicht auch für gendaylit benutzt?

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

        working_folder = UserPaths.bifacial_radiance_files_folder
        # check working folder
        fi.make_dirs_if_not_there(working_folder)

        # create Bifacial_Radiance Object with ground
        self.radObj = br.RadianceObj(s.name, path=str(working_folder))
        self.radObj.setGround(s.ground_albedo)

        # read TMY or EPW data
        if self.download_EPW is True:
            epw_file = self.radObj.getEPW(
                lat=s.apv_location.latitude,
                lon=s.apv_location.longitude)
            self.met_data = self.radObj.readEPW(epw_file)
        else:
            # ! noch statisch und provisorisch:
            weather_file = UserPaths.bifacial_radiance_files_folder /\
                Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')
            self.met_data = self.radObj.readWeatherFile(
                weatherFile=str(weather_file))

        # read and create PV module
        if self.cellLevelModule is True:
            with open('configs\apv_morschenich.json') as f:
                configs = json.load(f)
                cellLevelModuleParams = configs['cellLevelModuleParams']
                print(cellLevelModuleParams)
                self.radObj.makeModule(
                    name=s.module_type,
                    **moduleDict,
                    cellLevelModuleParams=cellLevelModuleParams)

        else:
            self.radObj.makeModule(name=s.module_type,
                                   x=moduleDict['x'],
                                   y=moduleDict['y'],)

        # create structure <To BE DEFINED LATER>

        # Create Sky

        timeindex = apv.utils.time.get_hour_of_year(self.sim_date_time)
        if self.sky_gen_type == 'gendaylit':
            # if s.start_time == '' and s.end_time == '':
            self.radObj.gendaylit(timeindex=timeindex)
            self.oct_file_name = self.radObj.name + '_' + self.sim_date_time
            self.scene = self.radObj.makeScene(moduletype=s.module_type,
                                               sceneDict=sceneDict)
            self.radObj.makeOct(  # self.radObj.getfilelist(), #passiert autom.
                octname=self.oct_file_name)

        '''
            else:
                begin = int(s.start_time)
                end = int(s.end_time) + 1
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


        elif self.sky_gen_type == 'gencumsky':
            self.radObj.genCumSky(epwfile=epw_file)
            self.scene = self.radObj.makeScene(moduletype=s.module_type,
                                               sceneDict=sceneDict)
            # bitte mehr kommentieren
            self.radObj.makeOct(self.radObj.getfilelist())
        '''
        return self.radObj, self.scene, self.oct_file_name, self.met_data

    def view_scene(
        self, view_name: str = 'total', oct_file_name=None
    ):
        """views an .oct file via radiance/bin/rvu.exe

        Args:
            view_name (str): select from ['total', ...]
            as defined in settings.scene_camera_dicts
            a .vp file will be stored with this name in
            e.g. 'C:\\Users\\Username\\agri-PV\\views\\total.vp'

            oct_fn (str): file name of the .oct file without extension
            being located in the view_fp parent directory (e.g. 'Demo1')
            Defaults to settings.Simulation.name.
        """

        if oct_file_name is None:
            oct_file_name = self.oct_file_name

        scd = s.scene_camera_dicts[view_name]

        for key in scd:
            scd[key] = str(scd[key])+' '

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

    def _calc_ground_grid_parameters(self):
        self.x_field: int = round(
            sceneDict['nMods'] * moduleDict['x']) + 2*2

        self.y_field: int = round(
            sceneDict['pitch'] * sceneDict['nRows']
            + moduleDict['y'] * moduleDict['numpanels']) + 2*2

        self.ygrid: list[float] = np.arange(
            -self.y_field / 2,
            (self.y_field / 2) + 1,
            s.spatial_resolution)

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
        groundscan['xinc'] = s.spatial_resolution
        groundscan['zstart'] = 0.05
        groundscan['zinc'] = 0
        groundscan['yinc'] = 0

        return groundscan

    # class Simulator():

    def ground_simulation(self, accuracy: str = s.ray_tracing_accuracy):
        """provides irradiation readings on ground in form of a Dataframe
        as per predefined resolution.

        Args:
            accuracy (str): 'high' or 'low'

        Returns:
            [type]: [description]
        """

        octfile = self.oct_file_name
        # add extension if not there:
        if octfile[-4] != '.oct':
            octfile += '.oct'

        # instantiate analysis
        analysis = br.AnalysisObj(
            octfile=octfile, name=self.radObj.name)

        # number of sensors on ground against y-axis (along x-axis)
        sensorsy = self.x_field / s.spatial_resolution
        if (sensorsy % 2) == 0:
            sensorsy += 1

        # start rough scan to define ground afterwards
        groundscan, backscan = analysis.moduleAnalysis(scene=self.scene,
                                                       sensorsy=sensorsy)

        groundscan = self._set_groundscan(groundscan)

        print('\n number of sensor points is {:.0f}'.format(
            sensorsy*len(self.ygrid)))
        # Analysis and Results on ground - Time elapsed for analysis shown
        tictoc = pytictoc.TicToc()
        tictoc.tic()
        # simulation time-stamp from settings

        '''
        if s.start_time and s.end_time != '':
            try:
                begin = int(s.start_time)
                end = int(s.end_time) + 1
            except ValueError:
                print('begin and end time must be integers between 0 and 8760')

        else:
            begin = int(s.hour_of_year)
            end = begin + 1
        '''

        # for timeindex in np.arange(begin, end, 1):
        # oct_file_name = radObj.name + '_{}'.format(timeindex)
        for i in self.ygrid:
            groundscan['ystart'] = i
            temp_name = self.radObj.name + "_groundscan" + '{:.3f}'.format(i)

            analysis.analysis(octfile,
                              temp_name,
                              groundscan,
                              backscan,
                              accuracy=accuracy)

        """achtung! geht bisher nur für 'gendaylit'
        wegen timeindex=s.hour_of_year
        für file name. Werde später filesinterface "append all in folder"
        benutzen, dann hat sich das problem von selbst erledigt.
        """
        # Merge results to create one complete ground DataFrame
        dfs = []
        fi.make_dirs_if_not_there(UserPaths.results_folder)

        for i in self.ygrid:
            print('reading...\n results\\irr_{}_groundscan{:.3f}.csv'
                  .format(self.radObj.name, i))

            file_to_add = br.load.read1Result(os.path.join(
                UserPaths.bifacial_radiance_files_folder,
                'results\\irr_{}_groundscan{:.3f}.csv'
                .format(self.radObj.name, i)))
            dfs.append(file_to_add)
        print('merging files...')
        groundscan = pd.concat(dfs)
        groundscan = groundscan.reset_index()
        groundscan = groundscan.rename(columns={'Wm2Front': 'Wm2Ground'})
        self.csv_file_name = self.oct_file_name+'.csv'
        groundscan.to_csv(self.csv_file_name)
        print('merged file saved as csv file in\
            {} !'.format(UserPaths.results_folder))
        # print('the tail of the data frame shows number of grid \
        #    points \n' + groundscan.tail())

        self.df_ground_results = br.load.read1Result(self.csv_file_name)
        print('#### Results:')
        print(self.df_ground_results)
        tictoc.toc()
