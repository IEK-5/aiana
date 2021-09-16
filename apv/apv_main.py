# #
from apv.utils import APV_evaluation


if __name__ == '__main__':
    from pathlib import Path
    import apv

    SimSettings = apv.settings.simulation.Simulation()
    APV_SystSettings = \
        apv.settings.apv_systems.Default()

    weather_file = apv.settings.user_pathes.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    brObj = apv.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings,
        # weather_file=weather_file  # downloading automatically without this
    )
    enrgyObj = apv.utils.APV_evaluation.Evaluate_APV(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings
    )

    # #
    brObj.setup_br()

    # #
    brObj.view_scene(
        view_name='total', view_type='perspective'
    )
    # #
    brObj.run_raytracing_simulation()
    # #
    brObj.plot_ground_insolation()
    # TODO why is there a darker line at the top? Edge of the ground?
    # #
    brObj.plot_ground_insolation(cm_unit='Shadow-Depth')
    # #
    # show result data frame
    brObj.df_ground_results
    # #


# #
