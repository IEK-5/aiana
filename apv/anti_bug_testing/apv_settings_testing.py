# #
if __name__ == '__main__':
    from apv.classes.br_wrapper import BR_Wrapper
    from apv.anti_bug_testing.tester import Tester
    from apv.settings.apv_system_settings import APV_Syst_InclinedTables_S_Morschenich

    testerObj = Tester(open_oct_viewer=True)
    # #
    # mounting structure
    module_to_post_distance_x_dict = {
        'framed_single_axes_ridgeRoofMods': 0.5,
        #'framed_single_axes': 0.5,
        #'inclined_tables': -0.5  # to avoid modules floating between posts
    }
    for mountingStructureType in module_to_post_distance_x_dict:
        s = testerObj.default_settings.apv
        s.mountingStructureType = mountingStructureType
        s.mountingStructureDict['module_to_post_distance_x'] = \
            module_to_post_distance_x_dict[mountingStructureType]
        testerObj._set_current_to_default_settings()

        testerObj.test_dictItems_seperately(
            "mountingStructureDict",
            {
                'n_apv_system_clones_in_x': 2,
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
             #'cell_gaps',
             'checker_board',
             #'none'
        ])
    # #
    # view system with default test settings
    BR_Wrapper(testerObj.settings).create_and_view_octfile_for_SceneInspection()
    # #
    # test apv system settings
    testerObj.test_dictItems_seperately("sceneDict", {'tilt': 70,
                                                      'pitch': 20,
                                                      'hub_height': 12,
                                                      'nMods': 10,
                                                      'nRows': 5})
    # TODO pytest angucken "hooks"

    # #
    # azimuth
    for azimuth in [90, 180, 270]:
        testerObj.test_dictItems_seperately("sceneDict", {'azimuth': azimuth},
                                            view_name="top_down")

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
                                         'ground_scan_shift_y': 9,
                                         'round_up_scan_edgeLengths': True
                                         })


    # #
    # test and time updateSkyOnly for Morschenich APV and view scene

    import pytictoc
    tictoc = pytictoc.TicToc()

    for updateSk in [False, True]:
        testerObj.settings.apv = APV_Syst_InclinedTables_S_Morschenich()
        brObj = BR_Wrapper(testerObj.settings)
        tictoc.tic()
        brObj.create_octfile(update_sky_only=updateSk)
        tictoc.toc()
        print('=================================')
    brObj.octFileObj.view_octfile()

    # #
    testerObj.view_in_rvu_then_in_acceleradRT()
