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
from aiana.classes.aiana_main import AianaMain
from aiana.anti_bug_testing.tester_class import Tester
from aiana.settings.apv_system_settings \
    import APV_Syst_InclinedTables_S_Morschenich
from aiana.utils import files_interface as fi

# use this to also execute single cells within the run_apv_test method to test
# only certain parts
if __name__ == '__main__':
    testerObj = Tester(mode='create_reference')
# #
# use this if you want to quickly view the geometry (maybe also reduce the sim
# setting spatial_resolution to have to render less sensor visualisations):
if __name__ == '__main__':
    testerObj = Tester(
        mode='create_reference', open_oct_viewer=True, run_simulation=False)

# #


def run_apv_test(**kwargs):
    """Runs all tests in one go. To execute only parts (cells) of this method,
    the IDE "VS code" can be used with "# #" as cell marker.

    **kwargs:
        mode (optional): Defaults to 'test'
        (which means 1. simulate 2. check and plot difference to reference)
            alternative: 'create_reference'

        open_oct_viewer (bool, optional): to check scene creation for each set.
        Viewer needs to be closed manualy. Defaults to False.

        default_settings (Settings, optional): Defaults to None (constructing
            automatically based on setting files)

        run_simulation (bool, optional): Defaults to True, can be set False,
            if only viewing is of interest.
    """
    testerObj = Tester(**kwargs)
    # #
    # testerObj = Tester(mode='create_reference')
    # testerObj.default_settings.sim.hours = [14]  # for easier visual checking

    # #
    testerObj.test_listItems_separately("module_form", ['std',
                                                        'cell_gaps',
                                                        'checker_board'
                                                        ])
    # #
    # test apv system settings
    testerObj.test_dictItems_separately("sceneDict", {'tilt': 70,
                                                      'pitch': 20,
                                                      'hub_height': 12,
                                                      'nMods': 10,
                                                      'nRows': 5})
    # TODO pytest angucken "hooks"

    # #
    testerObj.test_dictItems_separately("moduleDict", {'x': 0.5,
                                                       'y': 1,
                                                       'xgap': 1,
                                                       'ygap': 1,
                                                       # 'zgap': 1,
                                                       'numpanels': 4})
    # #
    testerObj.test_dictItems_separately("groundScanAreaDict", {'start_x': 0,
                                                               'start_y': 0,
                                                               'length_x': 9,
                                                               'length_y': 9,
                                                               'margin_x': 9,
                                                               'margin_y': 9,
                                                               'shift_x': 9,
                                                               'shift_y': 9
                                                               })
    # #
    # test with or without glass
    testerObj.test_inverted_bool_settings(['glass_modules'])
    # #
    ##
    # azimuth
    testerObj.overwrite_settings_by_default_settings()
    print('The local time for the sun position is set to',
          testerObj.settings._dt.sunpos_locTime_str, '\n',
          testerObj.settings._dt.sim_dt_naiv,
          testerObj.settings._dt.sim_dt_utc)
    #
    for azimuth in [90,  # 180, 270  # east, south, west
                    ]:
        testerObj.test_dictItems_separately("sceneDict", {'azimuth': azimuth},
                                            view_name="top_down")
    # #
    # mounting structure types
    mountingStructureTypes = ['none',
                              'framed_single_axes_ridgeRoofMods',
                              'inclined_tables',
                              # 'morschenich_fixed' does not make sense with
                              # other geometry settings set to test settings
                              ]

    for mountingStructureType in mountingStructureTypes:

        s = testerObj.default_settings.apv
        if mountingStructureType == 'inclined_tables':
            s.mountingStructureDict['module_to_post_distance_x'] = - 0.5
            # (to avoid modules floating between posts without connection)
        else:
            s.mountingStructureDict['module_to_post_distance_x'] = 0.5

        testerObj.overwrite_settings_by_default_settings()
        testerObj.test_listItems_separately(
            "mountingStructureType", [mountingStructureType])

    # (to set back)
    s.mountingStructureDict['module_to_post_distance_x'] = 0.5
    testerObj.overwrite_settings_by_default_settings()

    # #
    # mountingStructureDict
    testerObj.test_dictItems_separately(
        "mountingStructureDict",
        {
            'n_apv_system_clones_in_x': 3,
            'n_apv_system_clones_in_negative_x': 2,
            'material': 'black',
            'post_thickness_x': 1,
            'post_thickness_y': 1,
            'n_post_x': 3,
            'post_distance_x': 3,
            'inner_table_post_distance_y': 0.5,  # has no effect except:
            # mountingStructureType == 'inclined_table'
        }
    )

    # # #
    # # tictoc oct_file creation for Morschenich APV
    # # (1. scene without sky, 2. adding sky)

    # import pytictoc
    # tictoc = pytictoc.TicToc()

    # testerObj.settings.apv = APV_Syst_InclinedTables_S_Morschenich()
    # aiana = BR_Wrapper(testerObj.settings)
    # for method in [
    #         aiana.octFileObj.create_octfile_without_sky,
    #         aiana.octFileObj.add_sky_to_octfile]:
    #     tictoc.tic()
    #     method()
    #     tictoc.toc()
    #     print('=================================')

    # # #

# #
