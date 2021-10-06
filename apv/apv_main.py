# #
from apv.br_wrapper import BR_Wrapper


if __name__ == '__main__':
    from pathlib import Path
    import apv

    SimSettings = apv.settings.simulation.Simulation()
    APV_SystSettings = apv.settings.apv_systems.Default()
    brObj = apv.br_wrapper.BR_Wrapper(SimSettings, APV_SystSettings)
    brObj.setup_br()

    # #
    brObj.view_scene(
        view_name='top_down', view_type='parallel'
    )
# #
if __name__ == '__main__':
    brObj.run_raytracing_simulation()
    # #
    brObj.plot_ground_insolation()
    # #
    brObj.plot_ground_insolation(cm_unit='Shadow-Depth')
    # #
    # show result data frame
    brObj.df_ground_results
# #
if __name__ == '__main__':
    evalObj = apv.classes.APV_evaluation.APV_Evaluation(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings
    )
    evalObj.evaluate_APV()
