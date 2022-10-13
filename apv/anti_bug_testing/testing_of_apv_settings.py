# #

from apv.classes.br_wrapper import BR_Wrapper
from apv.anti_bug_testing.tester_class import Tester
from apv.settings.apv_system_settings import APV_Syst_InclinedTables_S_Morschenich


def run():
    testerObj = Tester(  # open_oct_viewer=True,
        mode='create_reference'
    )
    ##
    # azimuth
    # testerObj.default_settings.sim.hours = [14]  # for easier visual checking
    testerObj.set_current_to_default_settings()
    print('The local time for the sun position is set to',
          testerObj.settings._dt.sunpos_locTime_str, '\n',
          testerObj.settings._dt.sim_dt_naiv,
          testerObj.settings._dt.sim_dt_utc)
    #
    for azimuth in [90,  # 180, 270  # east, south, west
                    ]:
        testerObj.test_dictItems_seperately("sceneDict", {'azimuth': azimuth},
                                            view_name="top_down")
    # #
    # helper dict to modify the post_distnce in x direction
    # of the mounting structure for this test:
    module_to_post_distance_x_dict = {
        'framed_single_axes_ridgeRoofMods': 0.5,
        # 'framed_single_axes': 0.5,
        # 'inclined_tables': -0.5  # to avoid modules floating between posts
    }
    for mountingStructureType in module_to_post_distance_x_dict:
        s = testerObj.default_settings.apv
        s.mountingStructureType = mountingStructureType
        s.mountingStructureDict['module_to_post_distance_x'] = \
            module_to_post_distance_x_dict[mountingStructureType]
        testerObj.set_current_to_default_settings()

        testerObj.test_dictItems_seperately(
            "mountingStructureDict",
            {
                'n_apv_system_clones_in_x': 3,
                # 'n_apv_system_clones_in_negative_x': 2,
                # 'material': 'black',
                # 'post_thickness_x': 1,
                # 'post_thickness_y': 1,
                # 'n_post_x': 3,
                # 'post_distance_x': 3,
                # 'inner_table_post_distance_y': 0.5,  # only used by inclined_table
            }
        )
    # test module forms with and without glass
    # #
    for glass in [True,
                  False]:
        testerObj.change_default_Setting("glass_modules", glass)
        testerObj.test_listItems_seperately("module_form", [
            # 'std',
            # 'cell_gaps',
            'checker_board',
            # 'none'
        ])
    # #
    # test apv system settings
    testerObj.test_dictItems_seperately("sceneDict", {'tilt': 70,
                                                      'pitch': 20,
                                                      'hub_height': 12,
                                                      'nMods': 10,
                                                      'nRows': 5})
    # TODO pytest angucken "hooks"

    # #
    testerObj.test_dictItems_seperately("moduleDict", {'x': 0.5,
                                                       'y': 1,
                                                       'xgap': 1,
                                                       'ygap': 1,
                                                       'zgap': 1,
                                                       'numpanels': 4})
    # #
    testerObj.test_dictItems_seperately("gScanAreaDict",
                                        {'ground_scan_margin_x': 9,
                                            'ground_scan_margin_y': 9,
                                            'ground_scan_shift_x': 9,
                                            'ground_scan_shift_y': 9
                                         })

    # #
    # tictoc oct_file creation for Morschenich APV
    # (1. scene without sky, 2. adding sky)

    import pytictoc
    tictoc = pytictoc.TicToc()

    testerObj.settings.apv = APV_Syst_InclinedTables_S_Morschenich()
    brObj = BR_Wrapper(testerObj.settings)
    for method in [
            brObj.octFileObj.create_octfile_without_sky,
            brObj.octFileObj.add_sky_to_octfile]:
        tictoc.tic()
        method()
        tictoc.toc()
        print('=================================')
