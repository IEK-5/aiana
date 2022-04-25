# #
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.util_classes.settings_grouper import Settings
from apv.settings.sim_settings import SimSettings_ForTesting
from apv.settings.apv_systems import APV_Syst_InclinedTables_S_Morschenich
from apv.settings.apv_systems import APV_ForTesting


class Tester:
    """methods to loop through config settings step by step while
    resetting the other settings to the test default settings"""

    def __init__(self) -> None:
        self.settings = Settings()
        self._set_defaultTestSettings()

    def _set_defaultTestSettings(self):
        self.settings.apv = APV_ForTesting()
        self.settings.sim = SimSettings_ForTesting()

    def _view_oct_then_resetSettings(self):
        BR_Wrapper(self.settings).create_and_view_octfile()
        self._set_defaultTestSettings()

    def view_in_rvu_then_in_acceleradRT(self):
        # without acceleradRT
        self.settings.sim.use_acceleradRT_view = False
        BR_Wrapper(self.settings).create_and_view_octfile()
        # with acceleradRT
        self.settings.sim.use_acceleradRT_view = True
        BR_Wrapper(self.settings).create_and_view_octfile()

    def test_panelAzimuth(self, azimuths: list, north_arrow=True):
        self.settings.sim.sim_date_time = '06-15_14:00'
        print('sim_date_time set to 06-15_14:00')
        for azimuth in azimuths:
            self.settings.apv.sceneDict['azimuth'] = azimuth
            BR_Wrapper(self.settings).create_and_view_octfile(
                topDownParallel_view=True,
                add_NorthArrows=north_arrow)

    def test_sceneDict(self, test_sceneDict: dict):
        for key in test_sceneDict.keys():
            self.settings.apv.sceneDict[key] = test_sceneDict[key]
            self._view_oct_then_resetSettings()

    def test_moduleDict(self, moduleDict: dict):
        for key in moduleDict.keys():
            self.settings.apv.moduleDict[key] = moduleDict[key]
            self._view_oct_then_resetSettings()

    def test_mountingStructureDict(
            self, mounting_structure_types: list, mountingStructureDict: dict):
        """nested for-loops for type and dict"""
        for list_element in mounting_structure_types:
            for key in mountingStructureDict.keys():
                self.settings.apv.mounting_structure_type = list_element
                if self.settings.apv.mounting_structure_type == \
                        'inclined_tables':
                    self.settings.apv.mountingStructureDict[
                        'module_to_post_distance_x'] = -0.5
                self.settings.apv.mountingStructureDict[key] =\
                    mountingStructureDict[key]
                self._view_oct_then_resetSettings()

    def test_groundScanAreaDict(self, gScan_area: dict):
        for key in gScan_area.keys():
            self.settings.apv.gScan_area[key] = gScan_area[key]
            self._view_oct_then_resetSettings()

    def test_module_forms(self, glass=False):
        for module_form in ['cell_level',
                            'cell_level_checker_board',
                            'roof_for_EW',
                            # 'cell_level_roof_for_EW'
                            ]:
            self.settings.apv.glass_modules = glass
            self.settings.apv.module_form = module_form
            self._view_oct_then_resetSettings()


if __name__ == '__main__':
    testerObj = Tester()
    ##
    for glass in [  # False,
            True]:
        testerObj.test_module_forms(glass)

    # #
    # show Morschenich APV
    testerObj.settings.sim.spatial_resolution = 0.1
    testerObj.settings.apv = APV_Syst_InclinedTables_S_Morschenich()
    BR_Wrapper(testerObj.settings).create_and_view_octfile()
    testerObj.settings.apv = APV_ForTesting()  # reset
    # #
    testerObj.test_moduleDict({'x': 0.5,
                               'y': 1,
                               'xgap': 1,
                               'ygap': 1,
                               'zgap': 1,
                               'numpanels': 4})

    # #
    testerObj.test_groundScanAreaDict({
        'ground_scan_margin_x': 5,  # [m]
        'ground_scan_margin_y': 5,  # [m]
        'ground_scan_shift_x': 5,  # [m] positiv: towards east
        'ground_scan_shift_y': 5,  # [m] positiv: towards north
        'round_up_scan_area_edgeLengths': True  # round up to full meters
    })

    # #
    mounting_structure_types = [
        # 'none',
        'framed_single_axes',
        'inclined_tables',
    ]
    testerObj.test_mountingStructureDict(
        mounting_structure_types,
        {  # mountingStructureDict:
            'n_apv_system_clones_in_x': 1,
            'n_apv_system_clones_in_negative_x': 1,
            'material': 'black',
            'post_thickness_x': 1,
            'post_thickness_y': 1,
            'n_post_x': 3,
            'module_to_post_distance_x': 2,
            'post_distance_x': 2,
            'inner_table_post_distance_y': 0.5,  # only for inclined_table
        })
    # #
    testerObj.view_in_rvu_then_in_acceleradRT()
    # #
    testerObj.test_panelAzimuth([90, 180, 270])
# #
if __name__ == '__main__':
    testerObj = Tester()
    testerObj.test_sceneDict({'tilt': 70,
                              'pitch': 20,
                              'hub_height': 12,
                              'nMods': 10,
                              'nRows': 5
                              })

    # #
    # settings.apv.n_apv_system_clones_in_x = 2
