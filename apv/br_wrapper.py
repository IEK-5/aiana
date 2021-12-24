# #
''' Called by main.py with the needed parameters to set the neccessary
objects, create scene and run simulation with Bifacial_Radiance according
to presets in settings.py

TODO

---------------------
# module clone does not work anymore...

- remove apv system settings from br wrapper and access it via geomObj
- aufräumen, dokumentieren, codeinterne TODOs sichten

- apv evaluation angucken und verstehen (Leo)

- typical day of month (dummy day 15) optional in settings integrieren
(evt. dann doch nicht ein string für datum-uhrzeit
sondern year, month, day, hour, minute separat
angeben?)

- geometry_hanlder klassen attribute gruppieren?

- clones and periodic boundary conditions for azi <> 0, 180°

- east west: ohne east-west-beams, da sie langanhaltende schatten bewirken oder
würde man die brauchen zur Aussteifung des Parks?

-----------
- slice-off edges in scan field for azi <> 0, 180°? (different line scans,
    might be really difficult with pivot table later)

(- gendaylitmxt für kumulativen sky? Aber damit ermittlung von shadow duration
eh nicht möglich...)


------------
longterm:
- GPU 28x faster rtrace https://nljones.github.io/Accelerad/index.html
- implement 'module' scan_target ?
- implement era5 data (apv_evaluation: yield & weather_data: solar position)
- add diffusive glass to be used optional in checker board empty slots.
ref: Miskin2019 and
https://www.pv-magazine.com/2020/07/23/special-solar-panels-for-agrivoltaics/

(-bei azi 180°:
wedgeplot x-achse: y-position im field, y-achse: GHI, monat 1-12 untereinander)

- estimate costs of double sized checker boards for same electrical yield with
 improved shadow values and compare to std
- also compare normal sized with double sized checker board shadow maps"


'''
# import needed packages

from apv.utils import files_interface as fi
from apv.settings.simulation import Simulation
from apv.settings.apv_systems import Default as SystSettings
from apv.classes.geometries_handler import GeometriesHandler
from apv.classes.weather_data import WeatherData
from apv.classes.APV_evaluation import APV_Evaluation
from apv.classes.sim_datetime import SimDT

import apv.settings.user_paths as user_paths
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
import sys
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
            SimSettings: Simulation,
            APV_SystSettings: SystSettings,
            geomObj: GeometriesHandler = None,
            results_subfolder: Path = None,
            weatherData=None,
            # weather_file=None,  # to optionally skip epw download
            debug_mode=False
    ):
        self.SimSettings = SimSettings
        self.APV_SystSettings = APV_SystSettings

        if geomObj is None:
            self.geomObj = GeometriesHandler(APV_SystSettings, debug_mode)
        else:
            self.geomObj = geomObj

        self.simDT: SimDT = None

        self.evalObj: APV_Evaluation = APV_Evaluation(
            SimSettings=SimSettings,
            APV_SystSettings=APV_SystSettings,
            weatherData=weatherData
        )

        if weatherData is None:
            self.weatherData = WeatherData(self.SimSettings)
        else:
            self.weatherData = weatherData

        self.debug_mode = debug_mode

        self.radObj: br.RadianceObj = None
        self.scene: br.SceneObj = None
        self.analObj: br.AnalysisObj = None

        self.ygrid: list[int] = []
        self.groundscan = dict()
        self.frontscan = dict()

        self.df_ground_results = pd.DataFrame()
        self.results_subfolder = results_subfolder
        self.csv_parent_folder = Path()  # only for non cumulative (hourly)
        self.csv_file_path = Path()
        self.oct_file_name = str()
        self.file_name = str()  # for plot and csv file

    def setup_br(self, dni_singleValue=None, dhi_singleValue=None):
        self.simDT = SimDT(self.SimSettings)
        self.set_up_file_names_and_paths()
        # adjust, e.g. add cell sizes
        self.APV_SystSettings = apv.utils.settings_adjuster.adjust_settings(
            self.APV_SystSettings)

        # create a bifacial_radiance object
        self.radObj = br.RadianceObj(
            self.file_name, str(user_paths.bifacial_radiance_files_folder)
        )
        self.radObj.setGround(self.SimSettings.ground_albedo)
        self.create_sky(dni_single=dni_singleValue, dhi_single=dhi_singleValue)
        self.create_materials()
        self.create_geometries(APV_SystSettings=self.APV_SystSettings)
        self.set_up_AnalObj_and_groundscan()

    def set_up_file_names_and_paths(self):

        if self.results_subfolder is None:
            self.results_subfolder = user_paths.results_folder / Path(
                self.SimSettings.sim_name,
                self.APV_SystSettings.module_form
                + '_res-' + str(self.SimSettings.spatial_resolution)+'m'
                + '_step-' + str(self.SimSettings.time_step_in_minutes)+'min'
            )
        else:
            self.results_subfolder = self.results_subfolder

        self.file_name = self.SimSettings.sim_date_time.replace(':', 'h')
        self.oct_file_name = self.SimSettings.sim_name \
            + '_' + self.APV_SystSettings.module_form + '_' + self.file_name
        # set csv file path for saving final merged results
        self.csv_parent_folder: Path = self.results_subfolder / Path('data')
        self.csv_file_path: Path = self.csv_parent_folder / Path(
            'ground_results' + '_' + self.file_name + '.csv')

        # check folder existence
        fi.make_dirs_if_not_there([user_paths.bifacial_radiance_files_folder,
                                   user_paths.data_download_folder,
                                   user_paths.results_folder,
                                   self.results_subfolder,
                                   self.csv_parent_folder]
                                  )

    def create_sky(self, dni_single=None, dhi_single=None, tracked=False):
        """
        We z-rotate the sky instead of the panel for an easier easier setup of
        the mounting structure and the scan points.
        """

        # if self.SimSettings.sky_gen_mode == 'gendaylit':
        self.weatherData.set_dhi_dni_ghi_and_sunpos_to_simDT(self.simDT)
        # to be able to pass own dni/dhi values:
        if dni_single is None:
            dni_single = self.weatherData.dni
        if dhi_single is None:
            dhi_single = self.weatherData.dhi

        if tracked:
            correction_angle = 90  # copy from Leonhard, ISE for later
            # maybe - 90 as i changed formula from
            # sunaz - scene - correc
            # to sunaz - (scene - correc)
        else:
            correction_angle = 180  # this will make north into the top in rvu

        # we want modules face always to south in rvu (azi = 180°)
        # if panel azi is e.g. 200°, we rotate sky by -20°
        sunaz_modified = self.weatherData.sunaz\
            - (self.APV_SystSettings.sceneDict["azimuth"] - correction_angle)

        if dni_single == 0 and dhi_single == 0:
            sys.exit("""DNI and DHI are 0 within the last hour until the \
                time given in settings/simulation/sim_date_time.\
                \n--> Creating radiance files and view_scene() is not \
                possible without light. Please choose a different time.""")

        if self.weatherData.sunalt < 0:
            sys.exit("""Cannot handle negative sun alitudes.\
                \n--> Creating radiance files and view_scene() is not \
                possible without light. Please choose a different time.""")

        # gendaylit using Perez models for direct and diffuse components
        self.radObj.gendaylit2manual(dni_single, dhi_single,
                                     self.weatherData.sunalt, sunaz_modified)

    def makeCustomMaterial(
        self,
        mat_name: str,
        mat_type: Literal['glass', 'metal', 'plastic', 'trans'],
        R: float = 0, G: float = 0, B: float = 0,
        specularity: float = 0, roughness: float = 0,
        transmissivity: float = 0, transmitted_specularity: float = 0,
        rad_mat_file: Path = user_paths.bifacial_radiance_files_folder / Path(
            'materials/ground.rad')
    ):
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
            # check for extra new line at the end
            if lines_new[-1][-1:] == '\n':
                text = ''
            else:
                text = '\n'
            # number of modifiers needed by Radiance
            mods = {'glass': 3, 'metal': 5, 'plastic': 5, 'trans': 7}

            # create text for Radiance input:
            text += (f'\nvoid {mat_type} {mat_name}\n0\n0'
                     f'\n{mods[mat_type]} {R} {G} {B}')
            if mods[mat_type] > 3:
                text += f' {specularity} {roughness}'
            if mods[mat_type] > 5:
                text += f' {transmissivity} {transmitted_specularity}'
            if self.debug_mode:
                print(f"{print_string} custom material {mat_name}.")
            f.writelines(lines_new + [text])
            f.close()

    def create_materials(self):
        # self.makeCustomMaterial(mat_name='dark_glass', mat_type='glass',
        #                        R=0.6, G=0.6, B=0.6)
        self.makeCustomMaterial(
            mat_name='grass', mat_type='plastic',
            R=0.1, G=0.3, B=0.08,
            specularity=0.1,
            # self.SimSettings.ground_albedo,  # TODO
            # albedo hängt eigentlich auch von strahlungswinkel
            # und diffusen/direktem licht anteil ab
            # https://curry.eas.gatech.edu/Courses/6140/ency/Chapter9/Ency_Atmos/Reflectance_Albedo_Surface.pdf
            roughness=0.3)

    def apply_BRs_makeModule(self, ghObj: GeometriesHandler):
        # # create PV module
        # this is a bit nasty because we use self.radObj.makeModule()
        # to create std or cell_level module, whereby in this case
        # the "text" argument has to be None. For the other module forms,
        # which are not present in self.radObj.makeModule(), we use own methods

        module_text_dict = {
            'std': None,  # rad text is created by self.radObj.makeModule()
            'cell_level': None,  # as above
            'none': "",  # empty
            'cell_level_checker_board': ghObj.make_checked_module_text,
            'EW_fixed': ghObj.make_EW_module_text,
            'cell_level_EW_fixed': ghObj.make_cell_level_EW_module_text,
        }
        module_form = ghObj.APV_SystSettings.module_form
        if module_form in ['std', 'cell_level', 'none']:
            # pass dict value without calling
            module_text = module_text_dict[module_form]
        else:
            # pass dict value being a ghObj method with calling
            module_text = module_text_dict[module_form]()

        if module_form == 'cell_level':
            # then use bifacial radiance by passing cellLevelModuleParams
            cellParams = ghObj.APV_SystSettings.cellLevelModuleParams
        else:
            cellParams = None

        self.radObj.makeModule(
            name=ghObj.APV_SystSettings.module_name,
            **ghObj.APV_SystSettings.moduleDict,
            cellLevelModuleParams=cellParams,
            text=module_text,
            glass=ghObj.APV_SystSettings.glass_modules,
        )

    def create_geometries(self, APV_SystSettings: SystSettings):
        """creates pv modules and mounting structure (optional)"""

        ghObj = GeometriesHandler(APV_SystSettings, self.debug_mode)
        self.apply_BRs_makeModule(ghObj)
        # make scene
        # set azimuth to 0
        sceneDict = APV_SystSettings.sceneDict.copy()
        sceneDict['azimuth'] = 180  # always to bottom in rvu,
        # rotating sky instead
        self.scene = self.radObj.makeScene(
            moduletype=APV_SystSettings.module_name,
            sceneDict=sceneDict)

        self.appendtoScene_condensedVersion(
            customObjects=ghObj.customObjects,
            extra_radtext_dict=ghObj.radtext_to_apply_on_a_custom_object)
        self.radObj.makeOct(octname=self.oct_file_name)

    def appendtoScene_condensedVersion(
            self, customObjects: dict,
            extra_radtext_dict: dict):
        """
        customObjects: key: file-name, value: rad_text
        """
        for key in customObjects:
            rad_file_path = f'objects/{key}.rad'
            with open(rad_file_path, 'wb') as f:
                f.write(customObjects[key]().encode('ascii'))
                # TODO group text method and extra operation in code in one place
                # per object. but its very nested, how can it be done nicer?
            # write single object rad_file_pathes in a grouping rad_file
            # with an optional radiance text operation being applied on the
            # single object as a sub group:
            if key in extra_radtext_dict:
                extra_radtext = extra_radtext_dict[key]
            else:
                extra_radtext = "!xform "

            with open(self.scene.radfiles, 'a+') as f:
                f.write(f'\n{extra_radtext}{rad_file_path}')

            self.radObj.radfiles.append(rad_file_path)

        print("\nCreated custom object", rad_file_path)

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

        oct_file_name = oct_file_name or self.oct_file_name

        scd = self.APV_SystSettings.scene_camera_dicts[view_name]

        for key in scd:
            scd[key] = str(scd[key]) + ' '

        view_fp = user_paths.bifacial_radiance_files_folder / Path(
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

    def set_up_AnalObj_and_groundscan(self):
        # instantiate analysis
        self.analObj = br.AnalysisObj(
            octfile=self.oct_file_name+'.oct', name=self.radObj.name)

        # number of sensors on ground against y-axis (along x-axis)
        sensorsy = np.round(
            self.geomObj.x_field / self.SimSettings.spatial_resolution)
        if (sensorsy % 2) == 0:
            sensorsy += 1

        self.ygrid: list[float] = np.arange(
            self.geomObj.scan_area_anchor_y,
            (self.geomObj.scan_area_anchor_y + self.geomObj.y_field
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

        self.groundscan['xstart'] = self.geomObj.scan_area_anchor_x
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
        temp_results: Path = user_paths.bifacial_radiance_files_folder / Path(
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

    def merge_line_scans(self):
        """merge results to create one complete ground DataFrame
        """
        temp_results: Path = user_paths.bifacial_radiance_files_folder / Path(
            'results')
        df: pd.DataFrame = fi.df_from_file_or_folder(
            temp_results, append_all_in_folder=True,
            print_reading_messages=False)
        df = df.reset_index()
        df['time_local'] = self.simDT.sim_dt_local
        df['time_utc'] = self.simDT.sim_dt_utc_pd

        df = self.evalObj.add_PAR(df=df)
        df = self.evalObj.add_shadowdepth(
            df=df, SimSettings=self.SimSettings, cumulative=False)

        df.to_csv(self.csv_file_path)
        print(f'merged file saved in {self.csv_file_path}\n')
        self.df_ground_results = df

    def plot_ground_heatmap(
        self,
        df: pd.DataFrame = None,
        destination_folder: Path = None,
        file_name: str = None,
        cm_unit: str = None,
        cumulative: bool = None
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
                str(self.csv_file_path))

        if cm_unit is None:
            cm_unit = self.SimSettings.cm_quantity

        if cumulative is None:
            cumulative = self.SimSettings.cumulative

        ticklabels_skip_count_number = int(
            4/self.SimSettings.spatial_resolution)
        if ticklabels_skip_count_number < 2:
            ticklabels_skip_count_number = "auto"

        if self.SimSettings.sky_gen_mode == 'gendaylit' and not cumulative:
            title = (f'Module Form: {self.APV_SystSettings.module_form}\n'
                     f'Date & Time: {self.SimSettings.sim_date_time}\n'
                     f'Resolution: {self.SimSettings.spatial_resolution} m')
        else:
            title = (f'Module Form: {self.APV_SystSettings.module_form}\n'
                     f'From: [{self.SimSettings.startdt}] '
                     f'To: [{self.SimSettings.enddt}]\n'
                     f'Resolution: {self.SimSettings.spatial_resolution} m')

        label_and_cm_input: dict = self.evalObj.get_label_and_cm_input(
            cm_unit=cm_unit, cumulative=cumulative)

        fig = apv.utils.plots.plot_heatmap(
            df=df, x='x', y='y', z=label_and_cm_input['z'],
            cm=label_and_cm_input['colormap'],
            x_label='x [m]', y_label='y [m]',
            z_label=label_and_cm_input['z_label'],
            plot_title=title,
            ticklabels_skip_count_number=ticklabels_skip_count_number
        )

        fig.axes[1] = apv.utils.plots.add_north_arrow(
            fig.axes[1], self.APV_SystSettings.sceneDict['azimuth'])
        if file_name is None:
            file_name = self.file_name

        if destination_folder is None:
            destination_folder = self.results_subfolder
        apv.utils.files_interface.save_fig(
            fig,
            cm_unit+'_' + label_and_cm_input['z']+'_' + file_name,
            parent_folder_path=destination_folder,
            sub_folder_name='',
        )

# #
