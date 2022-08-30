# #
from pathlib import Path
import pandas as pd
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.util_classes.settings_grouper import Settings
import apv.utils.files_interface as fi
# #
if __name__ == '__main__':
    settings = Settings()

    settings.sim.results_subfolder = 'testing/reference'
    settings.sim.results_subfolder = 'testing'
    # #
    settings.sim.spatial_resolution = 0.2
    # optional accelerad if installed:
    settings.sim.use_acceleradRT_view = True
    settings.sim.use_accelerad_GPU_processing = True
    brObj = BR_Wrapper(settings)
    # brObj.create_and_view_octfile_for_SceneInspection()
    # #
    brObj.create_octfile_for_Simulation()
    for hour in [10, 16]:
        # set time with leading zeros for a correct file order
        settings.sim.sim_date_time = f'06-15_{hour:02}:00'
        brObj.update_timeStep_and_sky(settings)
        brObj.simulate_and_evaluate()
        brObj.plotterObj.ground_heatmap(cm_quantity='shadow_depth',
                                        north_arrow_xy_posi=(-0.44, 1.2))

# #

def substract_test_from_ref_data(csv_path: Path):
    csv_path_ref = csv_path.replace(
        settings.sim.results_subfolder,
        settings.sim.results_subfolder+'/reference')

    #csv_path_ref=csv_path_ref.replace('16h', '10h')

    df_test = fi.df_from_file_or_folder(csv_path)
    df_ref = fi.df_from_file_or_folder(csv_path_ref)
    df = df_ref.copy()
    for col in ['Wm2', 'PARGround', 'ShadowDepth']:
        try:
            df.loc[:, col] = df_test.loc[:, col]-df_ref.loc[:, col]
        except KeyError:
            raise Exception('Dataframe(s) empty, probably no ref data found.')

    return df


def plot_value_difference(cm_quantity='shadow_depth'):
    hour = 16

    # # get test result csv path (not need if done after sim directly,
    # # but this would make problems uppon reference creation)
    brObj.settings.sim.sim_date_time = f'06-15_{hour:02}:00'
    brObj.settings.set_names_and_paths()
    csv_path = str(brObj.settings.paths.csv_file_path)

    # get difference df to use as input for plotterObj.ground_heatmap
    df_dif = substract_test_from_ref_data(csv_path)

    destination_path = brObj.settings.paths.results_folder / 'difference' / Path(
        f'{brObj.settings.names.csv_fn_ext[:-4]}_{cm_quantity}.jpg'
    )

    brObj.plotterObj.ground_heatmap(
        df_dif,
        destination_file_path=destination_path,
        cm_quantity=cm_quantity)


plot_value_difference()

# #
df_dif = substract_test_from_ref_data(str(brObj.settings.paths.csv_file_path))
df_dif['ShadowDepth'].abs().mean()

# #
