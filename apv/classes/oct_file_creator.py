# #
'''
oct file = ...


'''
# import needed packages

import sys
import subprocess
from typing import Literal
from pathlib import Path

import bifacial_radiance as br
from apv.utils import radiance_utils
from apv.classes.weather_data import WeatherData
from apv.classes.util_classes.settings_grouper import Settings
from apv.classes.util_classes.geometries_handler import GeometriesHandler
# for testing
from apv.settings.apv_systems import APV_Syst_InclinedTables_S_Morschenich


class OctFileCreator:
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

    sceneObj: br.SceneObj  # set in create_oct_file()
    radianceObj: br.RadianceObj  # "
    moduleObj: br.ModuleObj

    def __init__(
            self,
            settings: Settings = None,
            weatherData: WeatherData = None,
            debug_mode=False
    ):

        if settings is None:  # for self.set_up_AnalObj_and_groundscan()
            self.settings = Settings()
        else:
            self.settings = settings

        if weatherData is None:
            self.weatherData = WeatherData(self.settings)
        else:
            self.weatherData = weatherData

        self.debug_mode = debug_mode
        # for custom radiance geometry descriptions:
        self.ghObj = GeometriesHandler(self.settings.apv, self.debug_mode)

    def create_oct_file(self):
        """creates pv modules and mounting structure (optional)"""

        # create a bifacial_radiance Radiance object
        self.radianceObj = br.RadianceObj(
            path=str(self.settings.paths.bifacial_radiance_files)
        )
        # make scene
        self._create_materials()
        self.radianceObj.setGround(self.settings.sim.ground_albedo)
        self._create_sky()

        # backup azimuth
        self.sceneDict = self.settings.apv.sceneDict.copy()
        azimuth = self.sceneDict["azimuth"]
        # set azimuth for BR to 180
        self.sceneDict['azimuth'] = 180  # always to bottom in rvu,
        # to handle azimuth, the sky was already rotated instead

        customObjects = {'modules': self.get_radtext_of_all_modules}
        # north arrow
        if self.debug_mode:
            customObjects['north_arrow'] = self.ghObj.north_arrow

        # scan area
        if self.settings.apv.add_groundScanArea_as_object_to_scene:
            customObjects['scan_area'] = self.ghObj.groundscan_area

        # mounting structure
        structure_type = self.settings.apv.mounting_structure_type
        if structure_type == 'declined_tables':
            customObjects['structure'] = self.ghObj.declined_tables_mount
        elif structure_type == 'framed_single_axes':
            customObjects['structure'] = self.ghObj.framed_single_axes_mount

        cloning_rad_text = self.ghObj.get_rad_txt_for_cloning_of_the_apv_system()
        extra_radtext_to_apply_on_a_radObject = {
            'north_arrow': f'!xform -rz {azimuth-180} -t 10 10 0 ',
            'structure': cloning_rad_text,
            'modules': cloning_rad_text,
        }

        self._appendtoScene_condensedVersion(  # mounting structure, ground, etc
            customObjects, extra_radtext_to_apply_on_a_radObject
        )

        self.radianceObj.makeOct(octname=self.settings.names.oct_fn[:-4])

    def view_scene(
        self,
        view_type: Literal['perspective', 'parallel'] = 'perspective',
        view_name: Literal['total', 'module_zoom', 'top_down'] = 'total',
        oct_file_name=None
    ):
        """views an .oct file via radiance/bin/rvu.exe

        Args:
            view_type (str): 'perspective' or 'parallel'

            view_name (str): select from ['total', ...]
                as defined in settings.scene_camera_dicts
                a .vp file containing the sttings will be stored with this name
                in e.g. 'C:\\Users\\Username\\agri-PV\\views\\total.vp'

            oct_file_name (str): file name of the .oct file without extension
                being located in the view_fp parent directory (e.g. 'Demo1')

            """
        view_fp = self.settings.paths.bifacial_radiance_files / Path(
            'views/'+view_name+'.vp')
        scd = self.settings.apv.scene_camera_dicts[view_name]
        radiance_utils.write_viewfile_in_vp_format(scd, view_fp, view_type)

        if oct_file_name is None:
            oct_file_name = self.settings.names.oct_fn

        print(f'Viewing {oct_file_name}.')
        subprocess.call(
            ['rvu', '-vf', view_fp, '-e', '.01', oct_file_name])

    def _create_materials(self):
        # self.makeCustomMaterial(mat_name='dark_glass', mat_type='glass',
        #                        R=0.6, G=0.6, B=0.6)
        rad_mat_file = self.settings.paths.bifacial_radiance_files \
            / Path('materials/ground.rad')
        radiance_utils.makeCustomMaterial(
            rad_mat_file,
            mat_name='grass', mat_type='plastic',
            R=0.1, G=0.3, B=0.08,
            specularity=0.1,
            # self.settings.sim.ground_albedo,  # TODO
            # albedo hängt eigentlich auch von strahlungswinkel
            # und diffusen/direktem licht anteil ab
            # https://curry.eas.gatech.edu/Courses/6140/ency/Chapter9 \
            # /Ency_Atmos/Reflectance_Albedo_Surface.pdf
            roughness=0.3)

    def _create_sky(self, tracked=False):
        """
        We z-rotate the sky instead of the panel for an easier easier setup of
        the mounting structure and the scan points.
        """

        if tracked:
            correction_angle = 90  # copy from Leonhard, ISE for later
            # maybe - 90 as i changed formula from
            # sunaz - scene - correc
            # to sunaz - (scene - correc)
        else:
            correction_angle = 180  # this will make north into the top in rvu

        # we want modules face always to south in rvu (azi = 180°)
        # if panel azi is e.g. 200°, we rotate sky by -20°
        sunaz_modified = self.weatherData.sunaz + correction_angle\
            - self.settings.apv.sceneDict["azimuth"]

        if self.weatherData.dni == 0 and self.weatherData.dhi == 0:
            sys.exit("""DNI and DHI are 0 within the last hour until the \
                time given in settings/simulation/sim_date_time.\
                \n--> Creating radiance files and view_scene() is not \
                possible without light. Please choose a different time.""")

        if self.weatherData.sunalt < 0:
            sys.exit("""Cannot handle negative sun alitudes.\
                \n--> Creating radiance files and view_scene() is not \
                possible without light. Please choose a different time.""")

        # gendaylit using Perez models for direct and diffuse components
        self.radianceObj.gendaylit2manual(
            self.weatherData.dni, self.weatherData.dhi,
            self.weatherData.sunalt, sunaz_modified)

    def get_radtext_of_all_modules(self):
        # # create PV module
        # this is a bit nasty because we use self.radObj.makeModule()
        # to create std or cell_level module, whereby in this case
        # the "text" argument has to be None. For the other module forms,
        # which are not present in self.radObj.makeModule(), we use own methods

        single_module_text_dict = {
            'std': None,  # rad text is created by self.radObj.makeModule()
            'cell_level': None,  # as above
            'none': "",  # empty
            'cell_level_checker_board': self.ghObj.make_checked_module_text,
            'EW_fixed': self.ghObj.make_EW_module_text,
            'cell_level_EW_fixed': self.ghObj.make_cell_level_EW_module_text,
        }
        module_form = self.settings.apv.module_form
        if module_form in ['std', 'cell_level', 'none']:
            # pass dict value without calling
            single_module_text = single_module_text_dict[module_form]
        else:
            # pass dict value being a ghObj-method with calling
            single_module_text = single_module_text_dict[module_form]()

        self.moduleObj = br.ModuleObj(
            name=self.settings.apv.module_name,
            **self.settings.apv.moduleDict,
            text=single_module_text,
            glass=self.settings.apv.glass_modules,
            # TODO check frame and omega input options
        )

        if module_form == 'cell_level':
            self.moduleObj.addCellModule(
                self.settings.apv.cellLevelModuleParams)

        self.sceneObj = self.radianceObj.makeScene(
            module=self.moduleObj, sceneDict=self.sceneDict
        )

        modules_text = (
            self.moduleObj.text  # text of module radiance description
            # (only "numpanels" considered)
            + self.sceneObj.text.replace(  # all modules in first set
                '!xform', '|xform').replace(
                f' objects\\{self.settings.apv.module_name}.rad', ''))

        return modules_text

    def _appendtoScene_condensedVersion(
            self, customObjects: dict,
            extra_radtext_dict: dict):
        """
        customObjects: key: file-name, value: rad_text
        """
        for key in customObjects:
            rad_file_path = f'objects/{key}.rad'
            with open(rad_file_path, 'wb') as f:
                f.write(customObjects[key]().encode('ascii'))

            # write single object rad_file_pathes in a grouping rad_file
            # with an optional radiance text operation being applied on the
            # single object as a sub group:
            if key in extra_radtext_dict:
                extra_radtext = extra_radtext_dict[key]
            else:
                extra_radtext = "!xform "

            with open(self.sceneObj.radfiles, 'a+') as f:
                f.write(f'\n{extra_radtext}{rad_file_path}')

            self.radianceObj.radfiles.append(rad_file_path)

        print("\nCreated custom object", rad_file_path)


# #
# testing
if __name__ == '__main__':
    # azimuth and cloning
    octFileCreator = OctFileCreator(debug_mode=True)
    #octFileCreator.settings.apv.n_apv_system_clones_in_negative_x = 1
    for azimuth in [180]:  # [90, 135, 180, 270]:
        #octFileCreator.settings.apv = APV_Syst_InclinedTables_S_Morschenich()
        octFileCreator.settings.apv.sceneDict['azimuth'] = azimuth
        octFileCreator.create_oct_file()
        octFileCreator.view_scene(
            # view_name='top_down', view_type='parallel'
        )

# #
