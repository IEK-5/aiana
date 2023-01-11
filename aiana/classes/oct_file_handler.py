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
# #
import time
from frads import util
import subprocess as sp
from typing import Literal
from pathlib import Path
from aiana.classes.util_classes.print_hider import PrintHider

import bifacial_radiance as br
from aiana.utils import radiance_utils
from aiana.classes.weather_data import WeatherData
from aiana.classes.util_classes.settings_handler import Settings
from aiana.classes.rad_txt_related.geometries_handler import GeometriesHandler
# for testing
from aiana.settings.apv_system_settings import APV_Syst_InclinedTables_S_Morschenich

import logging
logger = logging.getLogger("aiana.OctFileHandler")


class OctFileHandler:
    """
    to create and views *.oct files, takes as input:
        - a settings-object
        - a weatherData-object containing the correct irradiance and sun
            position based on the time settings in sim_settings, and
        - a geometries_handler-object, which creates based on the apv_system
            settings rad-files (Radiance text file format for geometries)

    NOTE: if tracking is included in future, the modules needs to be shifted
    from octfile_without_sky to octfile_with_sky (maybe rename stationary_parts
    and transient_parts)
    """

    radianceObj: br.RadianceObj
    sceneObj: br.SceneObj  # set in create_octfile_without_sky()

    def __init__(
            self,
            settings: Settings,
            weatherData: WeatherData,
            ghObj: GeometriesHandler,
            debug_mode=False,
    ):
        self.settings = settings
        self.weatherData = weatherData
        self.ghObj = ghObj  # for custom radiance geometry descriptions
        self.debug_mode = debug_mode

        self.radianceObj = br.RadianceObj(
            path=str(self.settings._paths.radiance_input_files)
        )
        self.radianceObj.setGround(self.settings.sim.ground_albedo)
        # ground only needed for sky, but needs to be set only once
        # for all timesteps as we dont use dynamic albedo yet,
        # so it is done here but can become a TODO later
        self._create_materials()

    def create_octfile_without_sky(self, **kwargs):
        """creates pv modules and mounting structure (optional)
        so sky with ground is added later

        rad manual for -oconv:
        https://floyd.lbl.gov/radiance/man_html/oconv.1.html

        **kwargs:
        add_groundScanArea=False, add_NorthArrow=False,
            add_sensor_vis=False
        """

        # backup azimuth
        self.sceneDict = self.settings.apv.sceneDict.copy()
        azimuth = self.sceneDict["azimuth"]
        # set azimuth for BR to 180
        self.sceneDict['azimuth'] = 180
        # to handle azimuth, we rotate the sky instead, which makes geometry
        # description and result plotting much easier

        # modules and scene
        self.ghObj.create_module_radtext()
        self.sceneObj: br.SceneObj = self.radianceObj.makeScene(
            module=self.ghObj.moduleObj, sceneDict=self.sceneDict
        )

        # for mounting structure, ground, etc.:
        self._appendtoScene_condensedVersion(
            self.ghObj.get_customObjects(**kwargs),
            self.ghObj.get_customObj_transformations(azimuth)
        )

        # # # # create oct file without sky
        # to avoid the error: "fatal - boundary does not encompass scene",
        # when adding the larger sky to the scene, a boundary box with
        # the -b option needs to be defined:
        size = '400'
        xyz_min = '-200'

        cmd = ['oconv', '-b', xyz_min, xyz_min, xyz_min, size,
               '-f'  # this option freezes the stationary scene parts so when
               # re-using it for the transient parts (sky,...) it does not need
               # to be build again, solving the modname0.rad empty file error
               # and reduces the duration for adding sky later to 0.2 seconds)
               #'-r', 40000,
               ] \
            + self.radianceObj.materialfiles \
            + self.radianceObj.radfiles

        oconv_result = self._call_cmd_and_return_result(cmd)
        with open(self.settings._paths.oct_fp_noSky, 'wb') as w:
            # mode 'w+b' opens and truncates the file to 0 bytes
            w.write(oconv_result)
            w.close()

    def _call_cmd_and_return_result(
            self, cmd, count=5) -> bytes:
        """trying optionally several times as rarely xform fails,
        maybe because sub rad files are not yet closed although they should be
        """
        logger.debug(cmd)

        for i in range(count):
            proc = sp.run(cmd, input=None, stderr=sp.PIPE, stdout=sp.PIPE)
            if proc.stderr != b'':  # b for conversion to a sequence of octets
                # (integers between 0 and 255)
                if b'xform' in proc.stderr:
                    logger.warning(proc.stderr)
                    print(f'trying to build oct file again... {i+1}. time\n')
                    time.sleep(1)
                elif b'gendaylit' in proc.stderr:
                    return proc.stdout
                    # TODO gendaylit warning about actual radiance seems
                    # not to affect the results, but where does it come from?
                else:
                    logger.warning(proc.stderr)

            else:
                return proc.stdout
        raise Exception(
            'Oconv failed several times, maybe the rad file syntax is wrong?')

    def add_sky_to_octfile(self):
        # sky file name and sky creation
        sky_fn: str = self.create_sky()
        sky_fp: Path = self.settings._paths.radiance_input_files / sky_fn
        # NOTE the '-i' option is needed to add something to an existing oct
        cmd = ['oconv', '-i', self.settings._paths.oct_fp_noSky, sky_fp]

        oconv_result = self._call_cmd_and_return_result(cmd)
        with open(self.settings._paths.oct_fp, 'wb') as w:
            w.write(oconv_result)
            w.close()

    def view_octfile(
        self,
        view_type: Literal['perspective', 'parallel'] = 'perspective',
        view_name: Literal['total', 'close_up', 'top_down'] = 'total',
        oct_file_name=None,
        # use_rpict=False,
        screenshot_filepath=None
    ):
        """views an .oct file via radiance/bin/rvu.exe

        Args:
            view_type(str): 'perspective' or 'parallel'

            view_name(str): select from ['total', ...]as defined in
                settings.scene_camera_dicts.
                A .vp file containing the settings will be stored with this
                name in e.g. 'C:\\Users\\Username\\agri-PV\\views\\total.vp'

            oct_file_name(str): file name of the .oct file without extension
                being located in the view_fp parent directory

            """

        file_format = 'vf' if self.settings.view.use_acceleradRT_view else 'vp'

        view_fp = self.settings._paths.radiance_input_files / Path(
            f'views/{view_name}.{file_format}')
        try:
            scd = self.settings.view.scene_camera_dicts[view_name]
        except KeyError:
            print('KeyError - available keys are: ',
                  self.settings.view.scene_camera_dicts.keys())

        radiance_utils.write_viewfile_in_vp_format(scd, view_fp, view_type)

        if oct_file_name is None:
            oct_file_name = self.settings._names.oct_fn

        pr_str = ''  # with rpict' if use_rpict else ''
        print(f'Viewing {oct_file_name}{pr_str}.')

        y = self.settings.view.accelerad_img_height
        x = int(y / scd['vertical_view_angle'] * scd['horizontal_view_angle'])
        # if use_rpict:
        #     pic_fn = oct_file_name.replace('.oct', '.hdr')
        #     if self.settings.sim.use_accelerad_GPU_processing:
        #         prefix = 'accelerad_'
        #     else:
        #         prefix = ''
        #     cmd = [f'{prefix}rpict',  '-x', str(x), '-y', str(y),
        #            '-vf', view_fp, oct_file_name,
        #            '>', f'images/{pic_fn}']

        # rpict - x 4800 - y 4800 - i - ps 1 - dp 530 - ar 964 - ds 0.016 - dj 1 - dt 0.03 - dc 0.9 - dr 5 - st 0.12 - ab 5 - aa 0.11 - ad 5800 - as 5800 - av 25 25 25 - lr 14 - lw 0.0002 - vf render.vf bifacial_example.oct > render.hdr

        # os.system("rpict -dp 256 -ar 48 -ms 1 -ds .2 -dj .9 -dt .1 "+
        #       "-dc .5 -dr 1 -ss 1 -st .1 -ab 3  -aa .1 "+
        #       "-ad 1536 -as 392 -av 25 25 25 -lr 8 -lw 1e-4 -vf views/"
        #       +viewfile+ " " + octfile +
        #       " > images/"+name+viewfile[:-3] +".hdr")

        # TODO try _popen (move it to utils from simulator) to see error message
        if self.settings.view.use_acceleradRT_view:
            cmd = ['AcceleradRT', '-vf', view_fp, '-ab', '3', '-aa', '0',
                   '-ad', '1', '-x', str(x), '-y', str(y), '-s', '10000',
                   '-log', '0',  # turns off log scale of contrast
                   '-f-',  # turn false color off, default: on (-f+)
                   # https://nljones.github.io/Accelerad/rt.html#commandline
                   oct_file_name]
        else:
            cmd = ['rvu', '-vf', view_fp, '-e', '.01', oct_file_name]
        # call to wait until subprocess is finished
        sp.call(cmd)

    def _create_materials(self):
        # self.makeCustomMaterial(mat_name='dark_glass', mat_type='glass',
        #                        R=0.6, G=0.6, B=0.6)
        rad_mat_file = self.settings._paths.radiance_input_files \
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

        radiance_utils.makeCustomMaterial(
            rad_mat_file,
            mat_name='black', mat_type='plastic',
            R=0, G=0, B=0.001)  # bifacial_radiance overwrite for a bit pv blue

        radiance_utils.makeCustomMaterial(
            rad_mat_file,
            mat_name='as_ground', mat_type='plastic',
            R=self.radianceObj.ground.Rrefl[0],
            G=self.radianceObj.ground.Grefl[0],
            B=self.radianceObj.ground.Brefl[0])

        radiance_utils.makeCustomMaterial(
            rad_mat_file,
            mat_name='trans_plastic',
            mat_type='trans',
            R=.8, G=.8, B=.9,
            specularity=.01,
            roughness=.04,
            transmissivity=1,
            transmitted_specularity=1
        )

    def create_sky(self, tracked=False) -> str:
        """
        We z-rotate the sky instead of the panel for an easier setup of
        the mounting structure and the scan points.

        Returns
            skyname (str): filename of the sky in the /skies directory
        """

        if tracked:
            correction_angle = 90
            # NOTE this is copy for later from Leonhard (ISE)
            # maybe it has to be "- 90" as i changed formula from
            # sunaz - scene - correc
            # to
            # sunaz - (scene - correc)
        else:
            correction_angle = 180  # this will make north into the top in rvu

        # we want north to be always ahead in front of us in view for azi = 180
        # if panel azi is e.g. 200°, we rotate sky by -20°
        sunaz_modified = self.weatherData.sunaz + correction_angle\
            - self.settings.apv.sceneDict["azimuth"]

        if self.weatherData.dni <= 0 and self.weatherData.dhi <= 0:
            raise ValueError("""DNI and DHI are <= 0!
                \n--> Creating radiance files and view_scene() is not
                possible without light. Maybe choose a different time
                or start over again with fresh interactive window?""")

        if self.weatherData.sunalt < 0:
            raise ValueError("""Cannot handle negative sun alitudes.\
                \n--> Creating radiance files and view_scene() is not \
                possible without light. Please choose a different time.""")
        else:
            if self.weatherData.sunaz != sunaz_modified:
                print('sun azimuth modified for sky rotation from:',
                      self.weatherData.sunaz, 'to:', sunaz_modified)
        # gendaylit using Perez models for direct and diffuse components

        return self.radianceObj.gendaylit2manual(
            self.weatherData.dni, self.weatherData.dhi,
            self.weatherData.sunalt, sunaz_modified)

    def _appendtoScene_condensedVersion(self, customObjects: dict,
                                        customObj_transformations: dict):
        """
        customObjects: key: file-name, value: rad_text
        customObj_transformations: optional additional transforming rad_text
        placed before a rad_file reference so it looks like e.g.
        '!xform -t 1 0 0 objects/customObj.rad'
        For easier understanding open the *.rad files in the folder
        radiance_input_files/objects with a text editor.

        this method creates first object/*.rad files for each custom object
        (structure, scan area etc.) and then append these to the grouping
        rad file (self.sceneObj.radfiles) used as input for the OCT file,
        where also the modules and its scene xform was written already
        in the first line by BR.
        """
        # NOTE
        # self.sceneObj.radfiles is a path
        # while
        # self.radianceObj.radfiles is a list ...
        for key in customObjects:
            # 1. create custom object rad file

            rad_file_path = f'objects/{key}.rad'
            with open(rad_file_path, 'wb') as f:
                f.write(customObjects[key]().encode('ascii'))
                f.close()

            # write single object rad_file_pathes in a grouping rad_file
            # with an optional radiance text operation being applied on the
            # single object as a sub group:
            if key in customObj_transformations:
                extra_radtext = customObj_transformations[key]
            else:
                extra_radtext = "!xform "

            # 2. add custom object rad file path to grouping rad file
            with open(self.sceneObj.radfiles, 'a+') as f:
                f.write(f'\n{extra_radtext}{rad_file_path}')
                f.close()

            self.radianceObj.radfiles.append(rad_file_path)

            print("Created custom ", rad_file_path)


# #
# testing
if __name__ == '__main__':
    # azimuth and cloning
    octFileCreator = OctFileHandler(debug_mode=True)
    # octFileCreator.settings.apv.n_apv_system_clones_in_negative_x = 1
    for azimuth in [180]:  # [90, 135, 180, 270]:
        # octFileCreator.settings.apv = APV_Syst_InclinedTables_S_Morschenich()
        octFileCreator.settings.apv.sceneDict['azimuth'] = azimuth
        octFileCreator.create_octfile_without_sky()
        octFileCreator.view_octfile(
            # view_name='top_down', view_type='parallel'
        )

# #
