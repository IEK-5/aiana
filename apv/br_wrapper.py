# #
''' Called by main.py with the needed parameters to set the neccessary
objects, create scene and run simulation with Bifacial_Radiance according
to presets in settings.py

TODO

- methode in br_wrapper einbinden, die 16 years TMY als UTC runteläd,
wenn noch nicht existent, und die sich über location mit tz das
2 spalten ghi dni file mit richtigen positionen erstellt
bzw. dazu mohds methode aufruft.
Zielpfad in data download. Wir geben dann Almed den pfad und das file
manuell, damit er sich nicht registrieren muss bei copernicus website
--> Leo

- aus zeitangabe in settings eine pandas.timestamp machen und dann mittels
dem pytz package in UTC umwandeln, um mittels pvlib den sonnenstand zu bekommen
der als input für gendaylit2manual benötigt wird (ich traue br.radObj.metdata
solpos über epw file nicht so ganz...)
in dem Zusammenhang auch klären: was genau hat es mit dem 30 min shift auf sich
(machen die das vielleicht um +-30 min um den angegebenen zeitpunkt eine stunde
zu betrachten? aber warum sollte dann die sonnen position -30 gesetzt werden)?

- wenn oben fertig: prüfen ob sonnenaufgangs und untergangszeiten passen

- print nachricht ausgeben wenn man view_scene ausführt obwohl dni und dhi = 0
(dann passiert nämlich nichts)

- aufräumen, dokumentieren...


'''
# import needed packages
from apv.utils import units_converter as uc
from apv.utils import files_interface as fi
from apv.settings.apv_systems import Default as APV_SystSettings
from apv.utils.GeometriesHandler import GeometriesHandler
from apv.utils.weather_data import WeatherData
import apv.settings.user_pathes as user_pathes
from apv.settings import apv_systems
import apv
from typing import Iterator, Literal
from datetime import datetime
from typing import Literal
from datetime import datetime as dt
import subprocess
# from pvlib import *
import numpy as np
import pandas as pd
import os
import pytictoc
from pathlib import Path
from tqdm.auto import trange
import concurrent.futures
import bifacial_radiance as br

# #


class BR_Wrapper:
    """
    Attributes:
        simSettings (apv.settings.simulation.Simulation):
        simulation settings object
        --------
        radObj (bifacial_radiance.RadianceObj): radiance object
        scene (bifacial_radiance.SceneObj): scene object
        oct_file_name (str): .oct file name with or without extension
        met_data(bifacial_radiance.MetObj): meterologic data object

        the ones above are retrieved from running setup_br()
        --------

        the ones above are calculated automatically on initialisation
        but the extra margin can be set automatically

    """

    def __init__(
            self,
            SimSettings=apv.settings.simulation.Simulation(),
            APV_SystSettings=apv.settings.apv_systems.Default(),
            weather_file=None,  # to optionally skip epw download
            debug_mode=False
            # create_oct_file=True
    ):
        self.SimSettings: apv.settings.simulation.Simulation = SimSettings
        self.APV_SystSettings: apv.settings.apv_systems.Default = \
            APV_SystSettings

        self.geomObj = GeometriesHandler(
            SimSettings, APV_SystSettings, debug_mode)
        self.weatherObj = WeatherData()

        self.weather_file_br_epw = weather_file
        self.debug_mode = debug_mode
        # self.create_oct_file = create_oct_file

        self.radObj: br.RadianceObj = None
        self.scene: br.SceneObj = None
        self.oct_file_name: str = None
        self.analObj: br.AnalysisObj = None

        self.ygrid: list[int] = []
        self.groundscan = dict()
        self.frontscan = dict()

        self.df_ground_results = pd.DataFrame()
        self.csv_file_name = str()

    def setup_br(self):
        """
        docstring noch veraltet

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

        self.APV_SystSettings = apv.utils.settings_adjuster.adjust_settings(
            self.APV_SystSettings)

        working_folder = user_pathes.bifacial_radiance_files_folder
        # check folder existence
        fi.make_dirs_if_not_there([working_folder,
                                   user_pathes.data_download_folder,
                                   user_pathes.results_folder])

        # create Bifacial_Radiance Object with ground
        self.radObj = br.RadianceObj(
            self.SimSettings.sim_name, path=str(working_folder))
        self.radObj.setGround(self.SimSettings.ground_albedo)

        self._load_weather_data_and_create_sky()

        # set csv file name
        # (placed here to allow for access also without a simulation run)
        self.csv_file_name = self.oct_file_name + '.csv'

        # create mounting structure (optional) and pv modules
        self._create_materials()
        self._create_geometries(APV_SystSettings=self.APV_SystSettings)

        self._set_up_AnalObj_and_groundscan()
        return

    def _load_weather_data_and_create_sky(
            self, dni_singleValue=None, dhi_singleValue=None):

        # we use bifacial_radiance to fill metdata for sun pos and alitude
        # from epw data and optional replace irradiation data by satellite
        # read TMY or EPW data
        """EPW Dos:
        https://www.nrel.gov/docs/fy08osti/43156.pdf
        https://bigladdersoftware.com/epx/docs/8-2/auxiliary-programs/epw-csv-format-inout.html
        """
        self.weather_file_br_epw = \
            self.weather_file_br_epw or self.radObj.getEPW(
                lat=self.SimSettings.apv_location.latitude,
                lon=self.SimSettings.apv_location.longitude)

        self.radObj.metdata = self.radObj.readWeatherFile(
            weatherFile=str(self.weather_file_br_epw))

        # optional replace irradiation data (and keep sol position):
        if self.SimSettings.irradiance_data_source == 'ADS_satellite':
            # download data for longest full year time span availible
            download_file_path = self.weatherObj.download_insolation_data(
                self.SimSettings.apv_location, '2005-01-01/2021-01-01', '1hour')
            # make own TMY data
            df_irradiance = self.weatherObj.satellite_irradiance_data_to_TMY(
                download_file_path)

            self.radObj.metdata.ghi = df_irradiance.ghi
            self.radObj.metdata.dhi = df_irradiance.dhi
            # for sky to untilted ground cos(tilt) = 1 and GHI = DNI + DHI ->
            self.radObj.metdata.dni = df_irradiance.ghi - df_irradiance.dhi

        # Create Sky
        # gendaylit using Perez models for direct and diffuse components
        if self.SimSettings.sky_gen_mode == 'gendaylit':
            timeindex = apv.utils.time.get_hour_of_year(
                self.SimSettings.sim_date_time)

            # to be able to pass own dni/dhi values:
            if dni_singleValue is None:
                dni_singleValue = self.radObj.metdata.dni[timeindex]
            if dhi_singleValue is None:
                dhi_singleValue = self.radObj.metdata.dhi[timeindex]
            solpos = self.radObj.metdata.solpos.iloc[timeindex]
            sunalt = float(solpos.elevation)
            sunaz = float(solpos.azimuth)-180.0
            self.radObj.gendaylit2manual(
                dni_singleValue, dhi_singleValue, sunalt, sunaz)

            self.oct_file_name = self.radObj.name \
                + '_' + self.SimSettings.sim_date_time

        # gencumskyself.met_data
        if self.SimSettings.sky_gen_mode == 'gencumsky':
            # from (year,month,day,hour)
            startdt = dt.strptime(self.SimSettings.startdt, '%m-%d_%Hh')
            # to (year,month,day,hour)
            enddt = dt.strptime(self.SimSettings.enddt, '%m-%d_%Hh')

            if self.SimSettings.irradiance_data_source == 'EPW':
                epwfile = str(self.weather_file_br_epw)
            elif self.SimSettings.irradiance_data_source == 'ADS_satellite':
                epwfile = 'satellite_weatherData/TMY_nearJuelichGermany.csv'
                # TODO make it automatic with mohds method

            self.radObj.genCumSky(epwfile=epwfile,
                                  startdt=startdt,
                                  enddt=enddt)

            self.oct_file_name = self.radObj.name \
                + '_' + 'Cumulative'

    @staticmethod
    def makeCustomMaterial(
        mat_name: str,
        mat_type: Literal['glass', 'metal', 'plastic', 'trans'],
        R: float = 0, G: float = 0, B: float = 0,
        specularity: float = 0, roughness: float = 0,
        transmissivity: float = 0, transmitted_specularity: float = 0,
        rad_mat_file: Path = user_pathes.bifacial_radiance_files_folder / Path(
            'materials/ground.rad')
    ):
        # TODO add diffusive glass to be used optional in
        # checker board empty slots. ref: Miskin2019
        """type trans = translucent plastic
        radiance materials documentation:
        https://floyd.lbl.gov/radiance/refer/ray.html#Materials"""

        # read old file
        with open(rad_mat_file, 'r') as f:
            lines: list = f.readlines()
            f.close()

        # write new file
        with open(rad_mat_file, 'w') as f:
            print_string = 'Creating'
            lines_new = lines
            for i, line in enumerate(lines):
                if mat_name in line:
                    print_string = 'Overwriting'
                    # slice away existing material
                    lines_new = lines[:i-1] + lines[i+4:]
                    break
            # number of modifiers needed by Radiance
            mods = {'glass': 3, 'metal': 5, 'plastic': 5, 'trans': 7}
            # Create text for Radiance input:
            text = (f'\nvoid {mat_type} {mat_name}\n0\n0'
                    f'\n{mods[mat_type]} {R} {G} {B}')
            if mods[mat_type] > 3:
                text += f' {specularity} {roughness}'
            if mods[mat_type] > 5:
                text += f' {transmissivity} {transmitted_specularity}'
            text += '\n'
            print(f"{print_string} custom material {mat_name}.")
            f.writelines(lines_new + [text])
            f.close()
        return

    def _create_materials(self):
        # self.makeCustomMaterial(mat_name='dark_glass', mat_type='glass',
        #                        R=0.6, G=0.6, B=0.6)
        self.makeCustomMaterial(
            mat_name='grass', mat_type='plastic',
            R=0.1, G=0.3, B=0.08,
            specularity=0.1,  # self.SimSettings.ground_albedo,  # TODO
            # albedo hängt eigentlich auch von strahlungswinkel
            # und diffusen/direktem licht anteil ab
            # https://curry.eas.gatech.edu/Courses/6140/ency/Chapter9/Ency_Atmos/Reflectance_Albedo_Surface.pdf
            roughness=0.3)

    def _create_geometries(self, APV_SystSettings: APV_SystSettings):
        """create mounting structure (optional), pv modules"""

        ghObj = GeometriesHandler(
            self.SimSettings, APV_SystSettings, self.debug_mode)
        ghObj._set_init_variables()

        ghModule = apv.utils.GeometriesHandler  # TODO replace with Obj

        # create PV module

        if APV_SystSettings.module_form == 'cell_level':
            # then use bifacial radiance by passing cellLevelModuleParams
            cellLevelModuleParams = APV_SystSettings.cellLevelModuleParams
        else:
            cellLevelModuleParams = None

        module_text_dict = {
            'std': None,  # rad text created by bifacial radiance
            'cell_level': None,  # rad text created by bifacial radiance
            'none': "",  # empty
            'cell_level_checker_board': ghModule.checked_module,
            'EW_fixed': ghModule.make_text_EW,
            'cell_level_EW_fixed': ghModule.cell_level_EW_fixed,
        }

        if APV_SystSettings.module_form in ['std', 'cell_level', 'none']:
            # pass dict value without calling
            module_text = module_text_dict[APV_SystSettings.module_form]
        else:
            cellLevelModuleParams = None
            # pass dict value being a ghObj method with calling
            module_text = module_text_dict[APV_SystSettings.module_form](
                APV_SystSettings
            )
        self.radObj.makeModule(
            name=APV_SystSettings.module_name,
            **APV_SystSettings.moduleDict,
            cellLevelModuleParams=cellLevelModuleParams,
            text=module_text,
            glass=APV_SystSettings.glass_modules,
        )

        # make scene
        self.scene = self.radObj.makeScene(
            moduletype=APV_SystSettings.module_name,
            sceneDict=APV_SystSettings.sceneDict)
        rad_text = ''
        structure_type = APV_SystSettings.mounting_structure_type
        # create mounting structure as custom object:
        if structure_type == 'declined_tables':
            rad_text = ghObj.declined_tables_mount(
                add_glass_box=APV_SystSettings.add_glass_box)
        elif structure_type == 'framed_single_axes':
            rad_text = ghObj.framed_single_axes_mount()
        if APV_SystSettings.extra_customObject_rad_text is not None:
            rad_text += APV_SystSettings.extra_customObject_rad_text

        if rad_text != '':
            rz = 180 - APV_SystSettings.sceneDict["azimuth"]
            # add mounting structure to the radObj with rotation
            self.radObj.appendtoScene(  # '\n' + text + ' ' + customObject
                radfile=self.scene.radfiles,
                customObject=self.radObj.makeCustomObject(
                    'structure', rad_text),
                text=f'!xform -rz {rz}'
            )

        # add ground scan area visualization to the radObj without rotation
        ground_rad_text = ghObj.groundscan_area()

        self.radObj.appendtoScene(  # '\n' + text + ' ' + customObject
            radfile=self.scene.radfiles,
            customObject=self.radObj.makeCustomObject(
                'scan_area', ground_rad_text),
            text='!xform '  # with text = '' (default) it does not work!
            # all scene objects are stored in
            # bifacial_radiance_files/objects/... e.g.
            # SUNFARMING_C_3.81425_rtr_10.00000_tilt_20.00000_10modsx3rows_...
            # within this file different custom .rad files are concatenated by
            # !xform object/customObjectName.rad
        )

        # make oct file
        self.radObj.makeOct(octname=self.oct_file_name)

    def view_scene(
        self,
        view_type: Literal['perspective', 'parallel'] = 'perspective',
        view_name: Literal['total', 'module_zoom', 'top_down'] = 'total',
        oct_file_name=None,
        tool='rvu'
    ):
        """views an .oct file via radiance/bin/rvu.exe

        options:
        https://floyd.lbl.gov/radianppce/man_html/rpict.1.html

        Args:
            view_name (str): select from ['total', ...]
            as defined in settingself.simSettings.scene_camera_dicts
            a .vp file will be stored with this name in
            e.g. 'C:\\Users\\Username\\agri-PV\\views\\total.vp'

            oct_fn (str): file name of the .oct file without extension
            being located in the view_fp parent directory (e.g. 'Demo1')
             """

        if oct_file_name is None:
            oct_file_name = self.oct_file_name

        scd = self.APV_SystSettings.scene_camera_dicts[view_name]

        for key in scd:
            scd[key] = str(scd[key]) + ' '

        view_fp = user_pathes.bifacial_radiance_files_folder / Path(
            'views/'+view_name+'.vp')

        if view_type == 'parallel':
            t = 'l'
        else:  # perspective
            t = 'v'

        with open(view_fp, 'w') as f:
            f.write(
                f'{tool} -vt{t} -vp '
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
                + '-vv '
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
        sensorsy = np.round(
            self.geomObj.x_field / self.SimSettings.spatial_resolution)
        if (sensorsy % 2) == 0:
            sensorsy += 1

        self.ygrid: list[float] = np.arange(
            self.geomObj.sw_corner_scan_y,
            (self.geomObj.sw_corner_scan_y + self.geomObj.y_field
             + self.SimSettings.spatial_resolution),
            self.SimSettings.spatial_resolution)

        print(f'\n sensor grid:\nx: {sensorsy}, y: {len(self.ygrid)}, '
              f'total: {sensorsy * len(self.ygrid)}')

        # start rough scan to define ground afterwards
        # groundscan, backscan = self.analObj.moduleAnalysis(scene=self.scene,
        #                                                   sensorsy=sensorsy)
        self.frontscan, self.backscan = self.analObj.moduleAnalysis(
            scene=self.scene, sensorsy=sensorsy)
        """Modifying the groundscan dictionary, except for 'ystart',
        which is set later by looping through ygrid.

        groundscan (dict): dictionary containing the XYZ-start and
        -increments values for a bifacial_radiance linescan.
        It describes where the virtual ray tracing sensors are placed.
        The origin (x=0, y=0) of the PV facility is in its center.
        """
        self.groundscan = self.frontscan

        self.groundscan['xstart'] = self.geomObj.sw_corner_scan_x
        self.groundscan['xinc'] = self.SimSettings.spatial_resolution
        self.groundscan['zstart'] = 0.05
        self.groundscan['zinc'] = 0
        self.groundscan['yinc'] = 0

    def _run_line_scan(self, y_start):

        if self.SimSettings.scan_target == 'module':
            self.groundscan = None
        elif self.SimSettings.scan_target == 'ground':
            self.groundscan['ystart'] = y_start

        temp_name = (f'{self.radObj.name}_{self.SimSettings.scan_target}_'
                     f'scan_{y_start:.3f}')

        self.analObj.analysis(self.oct_file_name+'.oct',
                              temp_name,
                              self.frontscan,
                              self.backscan,
                              self.groundscan,
                              accuracy=self.SimSettings.ray_tracing_accuracy)

        return f'y_start: {y_start} done.'

    def run_raytracing_simulation(self) -> pd.DataFrame:
        """provides irradiation readings on ground in form of a Dataframe
        as per predefined resolution.
        """

        # clear temporary line scan results from bifacial_results_folder
        temp_results: Path = user_pathes.bifacial_radiance_files_folder / Path(
            'results')
        fi.clear_folder_content(temp_results)

        # to measure elapsed time:
        tictoc = pytictoc.TicToc()
        tictoc.tic()

        if self.SimSettings.use_multi_processing:

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

        tictoc.toc()
        print('\n')

        self.merge_line_scans()
        return

    def merge_line_scans(self):
        """merge results to create one complete ground DataFrame
        """
        temp_results: Path = user_pathes.bifacial_radiance_files_folder / Path(
            'results')
        df_ground_results: pd.DataFrame = fi.df_from_file_or_folder(
            temp_results, append_all_in_folder=True,
            print_reading_messages=False)

        df_ground_results = df_ground_results.reset_index()

        # Path for saving final results
        f_result_path = os.path.join(user_pathes.results_folder,
                                     self.csv_file_name)
        df_ground_results.to_csv(f_result_path)
        print(f'merged file saved in {f_result_path}\n')
        self.df_ground_results = df_ground_results
        return

    def plot_ground_insolation(
        self,
        df=None,
        cm_unit: Literal['Irradiance', 'PAR', 'Shadow-Depth'] = None
    ):
        """plots the ground insolation as a heat map and saves it into
            the results/plots folder.

        Args:
            df (pd.DataFrame): if None, a df is created
            from the csv file name stored in an instance of this class.
            Defaults to None.
        """

        if df is None:
            df = apv.utils.files_interface.df_from_file_or_folder(
                apv.settings.user_pathes.results_folder / Path(
                    self.csv_file_name))
        if cm_unit is None:
            cm_unit = self.SimSettings.cm_unit

        ticklabels_skip_count_number = int(
            2/self.SimSettings.spatial_resolution)
        if ticklabels_skip_count_number < 2:
            ticklabels_skip_count_number = "auto"

        if self.SimSettings.sky_gen_mode == 'gendaylit':
            title = (f'Module Form: {self.APV_SystSettings.module_form}\n'
                     f'Date & Time: {self.SimSettings.sim_date_time}\n'
                     f'Resolution: {self.SimSettings.spatial_resolution} m')
        else:
            title = (f'Module Form: {self.APV_SystSettings.module_form}\n'
                     f'From: [{self.SimSettings.startdt}] '
                     f'To: [{self.SimSettings.enddt}]\n'
                     f'Resolution: {self.SimSettings.spatial_resolution} m')

        if cm_unit == 'PAR':
            df = uc.irradiance_to_PAR(df=df)
            f_result_path = os.path.join(user_pathes.results_folder,
                                         self.csv_file_name)
            df.to_csv(f_result_path)
            z = 'PARGround'
            colormap = 'YlOrBr'
            z_label = 'PAR [μmol quanta.m$^{-2}$.s$^{-1}$]'

        elif cm_unit == 'Shadow-Depth':
            df = uc.irradiance_to_shadowdepth(df=df,
                                              SimSettings=self.SimSettings)
            f_result_path = os.path.join(user_pathes.results_folder,
                                         self.csv_file_name)
            df.to_csv(f_result_path)
            z = 'ShadowDepth'
            colormap = 'viridis_r'
            z_label = 'Shadow-Depth [%]'
        else:
            z = 'Wm2'
            colormap = 'inferno'
            z_label = 'Irradiance on Ground [W m$^{-2}$]'
        fig = apv.utils.plots.plot_heatmap(
            df=df, x='x', y='y', z=z, cm=colormap,
            x_label='x [m]', y_label='y [m]',
            z_label=z_label,
            plot_title=title,
            ticklabels_skip_count_number=ticklabels_skip_count_number
        )

        fig.axes[1] = apv.utils.plots.add_north_arrow(
            fig.axes[1], self.APV_SystSettings.sceneDict['azimuth'])

        apv.utils.files_interface.save_fig(fig, self.oct_file_name+'_'+z)

# #
