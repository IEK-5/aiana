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
# import apv.bifacial_radiance.main as br
# import apv.bifacial_radiance.module as br_module
from apv.utils import radiance_utils
from apv.classes.weather_data import WeatherData
from apv.classes.util_classes.settings_grouper import Settings
from apv.classes.util_classes.geometries_handler import GeometriesHandler
# for testing
from apv.settings.apv_systems import APV_Syst_InclinedTables_S_Morschenich


class OctFileHandler:
    """
    Attributes:
        simSettings (apv.settings.sim_settings.Simulation):
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

    sceneObj: br.SceneObj  # set in get_radtext_of_all_modules
    moduleObj: br.ModuleObj  # "
    radianceObj: br.RadianceObj  # set in create_oct_file()

    def __init__(
            self,
            settings: Settings,
            weatherData: WeatherData,
            ghObj: GeometriesHandler,
            debug_mode=False,
    ):

        self.settings = settings
        self.weatherData = weatherData
        # for custom radiance geometry descriptions:
        self.ghObj = ghObj
        self.debug_mode = debug_mode
        self.groundScanArea_added = False

    def create_octfile(self, add_groundScanArea=False, add_NorthArrow=False):
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

        customObjects = {}
        # north arrow
        if self.settings.apv.module_form != 'none':
            customObjects['modules'] = self.get_radtext_of_all_modules

        if add_NorthArrow:
            customObjects['north_arrow'] = self.ghObj.north_arrow

        # scan area
        if add_groundScanArea:
            customObjects['scan_area'] = self.ghObj.groundscan_area_and_sensors
            self.groundScanArea_added = True
        else:
            self.groundScanArea_added = False

        # mounting structure
        structure_type = self.settings.apv.mounting_structure_type
        if structure_type == 'inclined_tables':
            customObjects['structure'] = self.ghObj.inclined_tables
        elif structure_type == 'morschenich_fixed':
            customObjects['structure'] = self.ghObj.morschenich_fixed
        elif structure_type == 'framed_single_axes':
            customObjects['structure'] = self.ghObj.framed_single_axes_mount
        # else: structure_type == 'none' --> add nothing

        cloning_rad_text = self.ghObj.get_rad_txt_for_cloning_the_apv_system()
        extra_radtext_to_apply_on_a_radObject = {
            'north_arrow': f'!xform -rz {azimuth-180} -t 10 10 0 ',
            'structure': cloning_rad_text,
            'modules': cloning_rad_text,
        }

        self._appendtoScene_condensedVersion(
            customObjects, extra_radtext_to_apply_on_a_radObject
        )  # for mounting structure, ground, etc

        self.radianceObj.makeOct(octname=self.settings.names.oct_fn[:-4])

    def view_octfile(
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

        file_format = 'vf' if self.settings.sim.use_acceleradRT_view else 'vp'

        view_fp = self.settings.paths.bifacial_radiance_files / Path(
            f'views/{view_name}.{file_format}')
        scd = self.settings.view.scene_camera_dicts[view_name]
        radiance_utils.write_viewfile_in_vp_format(scd, view_fp, view_type)

        if oct_file_name is None:
            oct_file_name = self.settings.names.oct_fn

        print(f'Viewing {oct_file_name}.')

        x = self.settings.view.accelerad_img_width
        y = int(x * scd['vertical_view_angle'] / scd['horizontal_view_angle'])
        if self.settings.sim.use_acceleradRT_view:
            subprocess.call(
                ['AcceleradRT', '-vf', view_fp, '-ab', '3', '-aa', '0',
                 '-ad', '1', '-x', str(x), '-y', str(y), '-s', '10000',
                 '-log', '0',  # turns off log scale of contrast
                 '-f-',  # turn false color off, default: on (-f+)
                 # https://nljones.github.io/Accelerad/rt.html#commandline
                 oct_file_name])
        else:
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
            specularity=0,
            # self.settings.sim.ground_albedo,  # TODO
            # albedo hängt eigentlich auch von strahlungswinkel
            # und diffusen/direktem licht anteil ab
            # https://curry.eas.gatech.edu/Courses/6140/ency/Chapter9 \
            # /Ency_Atmos/Reflectance_Albedo_Surface.pdf
            roughness=0.3)

        radiance_utils.makeCustomMaterial(
            rad_mat_file,
            mat_name='red', mat_type='plastic',
            R=1, G=0, B=0)

    def _create_sky(self, tracked=False):
        """
        We z-rotate the sky instead of the panel for an easier easier setup of
        the mounting structure and the scan points.
        """

        if tracked:
            correction_angle = 90
            # NOTE this is copy  for later from Leonhard (ISE)
            # maybe it has to be "- 90" as i changed formula from
            # sunaz - scene - correc
            # to sunaz - (scene - correc)
        else:
            correction_angle = 180  # this will make north into the top in rvu

        # we want north to be always ahead in front of us in view (azi = 180°)
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
        """
        This method is realy difficult to understand...
        but Bifacial_radiance is also complicated here and need to make it
        even more complicate to enter new functionality (checker board,
        set_cloning in x direction with gap between sets)

        in first step, custom_single_module_text_dict is created
        # this is a bit nasty because we use self.radObj.makeModule()
        # to create std or cell_level module, whereby in this case
        # the (custom) "text" argument has to be None. For the other module
        # forms, which are not present in self.radObj.makeModule(),
        # we use the own ghObj methods

        then we use BR to build the scene and extract partly rad texts out of
        BR objects to puzzle these together to what we want.

        Adding glass made it more complicated (see single_module_elements)
        There is probably nicer way of doing it, but it also will take time
        to figure it out.
        """

        custom_single_module_text_dict = {
            'std': None,  # rad text is created by self.radObj.makeModule()
            'cell_level': None,  # ""
            'none': "",  # empty
            'cell_level_checker_board': self.ghObj.make_checked_module_text,
            'roof_for_EW': self.ghObj.make_roof_module_text_for_EW,
            'cell_level_roof_for_EW': self.ghObj.make_cell_level_EW_module_text,
        }  # (only black part, no glass / omega etc.)

        module_form = self.settings.apv.module_form
        if module_form in ['std', 'cell_level', 'none']:
            # pass dict value without calling
            single_module_text = custom_single_module_text_dict[module_form]
        else:
            # pass dict value being a ghObj-method with calling
            single_module_text = custom_single_module_text_dict[module_form]()

        self.moduleObj = br.ModuleObj(
            name=self.settings.apv.module_name,
            **self.settings.apv.moduleDict,
            text=single_module_text,
            glass=self.settings.apv.glass_modules,
            # there are now also new frame and omega input options
        )

        if module_form == 'cell_level':
            self.moduleObj.addCellModule(
                **self.settings.apv.cellLevelModuleParams)

        self.sceneObj: br.SceneObj = self.radianceObj.makeScene(
            module=self.moduleObj, sceneDict=self.sceneDict
        )

        # # # get modules_text # # #
        single_module_elements: list = self.moduleObj.text.split('\r\n')
        # only "numpanels" considered (has PV, glass, omega... as elements)

        xform_text_to_BR_scene_modules = self.sceneObj.text.replace(
            '!xform', '|xform').replace(
            f' objects\\{self.settings.apv.module_name}.rad', '')

        # all modules in the original set (now cloneable in x):
        modules_text = ""
        for element in single_module_elements:
            modules_text += element + xform_text_to_BR_scene_modules
            if element != single_module_elements[-1]:
                modules_text += '\r\n'
        """
        so wäre eigentlich einfacher:
        modules_text = self.sceneObj.text

        aber dann kommt
        >> xform: cannot find file "objects/SUNFARMING.rad"

        und
        modules_text = self.sceneObj.text.replace(' objects\\', ' objects/')
        hilft leider auch nicht.  #TODO Warum?
        """

        return modules_text

    def _appendtoScene_condensedVersion(
            self, customObjects: dict,
            extra_radtext_dict: dict):
        """
        customObjects: key: file-name, value: rad_text
        """

        # self.radianceObj.radfiles = []  # TODO  get rid of doubled array origin modules...
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

            # NOTE
            # self.sceneObj.radfiles is a path
            # while
            # self.radianceObj.radfiles is a list ...

            with open(self.sceneObj.radfiles, 'a+') as f:
                f.write(f'\n{extra_radtext}{rad_file_path}')

            self.radianceObj.radfiles.append(rad_file_path)

            print("\nCreated custom object", rad_file_path)


# #
# testing
if __name__ == '__main__':
    # azimuth and cloning
    octFileCreator = OctFileHandler(debug_mode=True)
    # octFileCreator.settings.apv.n_apv_system_clones_in_negative_x = 1
    for azimuth in [180]:  # [90, 135, 180, 270]:
        # octFileCreator.settings.apv = APV_Syst_InclinedTables_S_Morschenich()
        octFileCreator.settings.apv.sceneDict['azimuth'] = azimuth
        octFileCreator.create_octfile()
        octFileCreator.view_octfile(
            # view_name='top_down', view_type='parallel'
        )

# #