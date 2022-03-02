# module form
# #
if __name__ == '__main__':
    import importlib as imp
    import apv
    from apv.settings import apv_systems

    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.classes.br_wrapper)

    SimSettings = apv.settings.sim_settings.Simulation()
    SimSettings.sim_name = 'functionality'

    # #
    APV_SystSettings = apv_systems.SimpleSingleCheckerBoard()
    for module_form in ['std', 'cell_level', 'cell_level_checker_board',
                        'EW_fixed',
                        'cell_level_EW_fixed',
                        'none']:
        APV_SystSettings.module_form = module_form

        brObj = apv.classes.br_wrapper.BR_Wrapper(
            SimSettings=SimSettings,
            APV_SystSettings=APV_SystSettings,
            debug_mode=False
        )

        brObj.setup_br()
        # evalObj.evaluate_APV(SimSettings=SimSettings)
        brObj.view_scene()

# #
# apv_systems
if __name__ == '__main__':
    import importlib as imp
    import apv
    from apv.settings import apv_systems

    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.classes.br_wrapper)

    SimSettings = apv.settings.sim_settings.Simulation()
    SimSettings.sim_name = 'c'

    for APV_SystSettings in [
        apv_systems.APV_Morchenich_Checkerboard(),
        apv_systems.Default(),
        apv_systems.APV_Morchenich_EastWest(),
        apv_systems.APV_Syst_InclinedTables_Juelich(),
        apv_systems.SimpleSingleCheckerBoard(),
    ]:

        brObj = apv.classes.br_wrapper.BR_Wrapper(
            SimSettings=SimSettings,
            APV_SystSettings=APV_SystSettings,
            debug_mode=False
        )

        brObj.setup_br(dni_singleValue=10, dhi_singleValue=50)
        # evalObj.evaluate_APV(SimSettings=SimSettings)
        brObj.view_scene()

# #
# - simulations test (niedrige auflösung)

# - plot test

# - evaluation test
