from aiana.classes.rad_txt_related.morschenich import Morschenich
from aiana.classes.rad_txt_related.geometry_basics import GeomBasics
from aiana.classes.util_classes.settings_handler import Settings

from aiana.classes.util_classes.print_hider import PrintHider

import bifacial_radiance as br


class GeometriesHandler(GeomBasics):
    """
    to create the radiance text string for the oct file builder
    methods are forwarded so that they are called only uppon using
    """

    moduleObj: br.ModuleObj  # set in get_radtext_of_all_modules

    def __init__(self, settings: Settings):
        super().__init__(settings)

    def morschenich_fixed(self) -> str:
        return Morschenich(self.settings).morschenich_fixed()

    def create_module_radtext(self) -> str:
        """
        This method is a bit difficult to understand as we partly use
        Bifacial_radiance and add new functionality (checker board, ridgeroof,
        or APV-system set cloning in x-direction with a gap between sets)

        In a first step, custom_single_module_text_dict is created. Later we
        will use br.ModuleObj() class to create a std or cell_gap module, for
        which the (custom) "text" argument has to be None (value of the dict).
        For the other module form(s), e.g. checker board we use own ghObj
        method(s), which are are called only if needed (not in dict definition)

        After using br.ModuleObj(), we extract the rad text and store it into
        a backup file "objects/{module_name}0.rad". It contains the module
        cells, and optional the glass, and the frame. This file is loaded into
        "objects/{module_name}.rad" without "0" to apply modifications (xform)
        for set cloning and optional ridge roof, using the backup as input.
        "objects/{module_name}.rad" is then used later by BR for
        the scene transformation (tilt, nRow, ...)"
        """

        custom_single_module_text_dict = {
            'std': None,  # rad text is created by self.radObj.makeModule()
            'cell_gaps': None,  # ""
            'checker_board': self.make_checked_module_text,
            'none': "",  # empty
        }  # (only black part, no glass / omega etc.)

        module_form = self.settings.apv.module_form
        if module_form in ['std', 'cell_gaps', 'none']:
            # pass dict value without calling
            single_module_text = custom_single_module_text_dict[module_form]
        else:
            # pass dict value being a method with calling
            # (usefull if more custom modules will be added again)
            single_module_text = custom_single_module_text_dict[module_form]()

        with PrintHider():  # hide custom text usage warning
            self.moduleObj = br.ModuleObj(
                name=self.settings.apv.module_name,
                **self.settings.apv.moduleDict,
                text=single_module_text,
                glass=self.settings.apv.glass_modules,
                # there are now also new frame and omega input options
            )

        if module_form == 'cell_gaps':
            self.moduleObj.addCellModule(
                **self.settings.apv.cellLevelModuleParams)

        if self.settings.apv.framed_modules:
            self.moduleObj.addFrame(
                frame_material='Metal_Grey', frame_thickness=0.05,
                frame_z=0.03, frame_width=0.05, recompile=True)

        # backup BRs original single module rad text as file with a "0" suffix:
        module_name0_relPath = f'objects/{self.settings.apv.module_name}0.rad'
        with open(module_name0_relPath, 'wb') as f:
            f.write(self.moduleObj.text.encode('ascii'))

        # modify module text and save to original name without "0"
        if self.settings.apv.module_form == 'none':
            module_text_modified = ''
        else:
            # NOTE (BR scene modification (tilt, nRow, ...) not yet applied)
            module_text_modified = \
                self.get_rad_txt_for_cloning_the_apv_system()\
                + self.get_rad_txt_for_ridgeRoofMods_xform() \
                + f' {self.settings.apv.module_name}0.rad'
        module_name_relPath = f'objects/{self.settings.apv.module_name}.rad'

        # store APV system-set cloned with optional ridgeRoof_modified
        # module_text (BR scene modification (tilt, nRow, ...) not yet applied)
        with open(module_name_relPath, 'wb') as f:
            f.write(module_text_modified.encode('ascii'))

    def get_customObjects(self, add_groundScanArea=False,
                          add_NorthArrow=False,
                          add_sensor_vis=False) -> dict[str, str]:
        customObjects = {}
        # scan area
        if add_groundScanArea:
            customObjects['scan_area'] = self.groundscan_area

        # north arrow
        if add_NorthArrow:
            customObjects['north_arrow'] = self.north_arrow

        # sensors
        if add_sensor_vis:
            customObjects['sensors'] = self.sensor_visualization

        # mounting structure
        structure_type = self.settings.apv.mountingStructureType
        if structure_type == 'inclined_tables':
            customObjects['structure'] = self.inclined_tables
        elif structure_type == 'morschenich_fixed':
            customObjects['structure'] = self.morschenich_fixed
        elif structure_type in [
                'framed_single_axes', 'framed_single_axes_ridgeRoofMods']:
            customObjects['structure'] = self.framed_single_axes_mount
        # else: structure_type == 'none' --> add nothing

        return customObjects

    def get_customObj_transformations(self, azimuth: float) -> dict[str, str]:
        # this is defined here to have it next to the customObjects dict def
        return {
            'north_arrow': f'!xform -rz {azimuth-180} -t 10 10 0 ',
            'structure': self.get_rad_txt_for_cloning_the_apv_system(),
            # cloning only the structure here,
            # the modules are cloned within self.create_module_radtext()
        }
