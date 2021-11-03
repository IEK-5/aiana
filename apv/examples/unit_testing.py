# #
if __name__ == '__main__':
    import importlib as imp
    import apv
    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.br_wrapper)

    SimSettings = apv.settings.simulation.Simulation()
    SimSettings.sim_name = 'unit_testing'
    APV_SystSettings = apv.settings.apv_systems.SimpleForCheckerBoard()

    # module form

    for module_form in [  # 'std','cell_level','cell_level_checker_board',
        # 'EW_fixed',
        'cell_level_EW_fixed',
            'none']:
        APV_SystSettings.module_form = module_form

        brObj = apv.br_wrapper.BR_Wrapper(
            SimSettings=SimSettings,
            APV_SystSettings=APV_SystSettings,
            debug_mode=False
        )

        brObj.setup_br()
        # evalObj.evaluate_APV(SimSettings=SimSettings)
        brObj.view_scene()

# #
