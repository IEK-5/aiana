# module form
# #
if __name__ == '__main__':
    import importlib as imp
    import aiana
    from aiana.settings import apv_system_settings

    imp.reload(aiana.classes.geometries_handler)
    imp.reload(aiana.settings.apv_systems)
    imp.reload(aiana.classes.br_wrapper)

    SimSettings = aiana.settings.sim_settings.Simulation()
    SimSettings.sim_name = 'functionality'

    # #
    APV_SystSettings = apv_system_settings.SimpleSingleCheckerBoard()
    for module_form in ['std', 'cell_gaps', 'checker_board',
                        'roof_for_EW',
                        'cell_gaps_roof_for_EW',
                        'none']:
        APV_SystSettings.module_form = module_form

        aiana = aiana.classes.br_wrapper.BR_Wrapper(
            SimSettings=SimSettings,
            APV_SystSettings=APV_SystSettings,
            debug_mode=False
        )

        aiana.setup_br()
        # evalObj.evaluate_APV(SimSettings=SimSettings)
        aiana.view_scene()

# #
# apv_systems
if __name__ == '__main__':
    import importlib as imp
    import aiana
    from aiana.settings import apv_system_settings

    imp.reload(aiana.classes.geometries_handler)
    imp.reload(aiana.settings.apv_systems)
    imp.reload(aiana.classes.br_wrapper)

    SimSettings = aiana.settings.sim_settings.Simulation()
    SimSettings.sim_name = 'c'

    for APV_SystSettings in [
        apv_system_settings.APV_Morchenich_Checkerboard(),
        apv_system_settings.APV_SettingsDefault(),
        apv_system_settings.APV_Morchenich_EastWest(),
        apv_system_settings.APV_Syst_InclinedTables_Juelich(),
        apv_system_settings.SimpleSingleCheckerBoard(),
    ]:

        aiana = aiana.classes.br_wrapper.BR_Wrapper(
            SimSettings=SimSettings,
            APV_SystSettings=APV_SystSettings,
            debug_mode=False
        )

        aiana.setup_br(dni_singleValue=10, dhi_singleValue=50)
        # evalObj.evaluate_APV(SimSettings=SimSettings)
        aiana.view_scene()

# #
# - simulations test (niedrige auflösung)

# - plot test

# - evaluation test
