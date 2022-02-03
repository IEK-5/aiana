"""This module contains project independent helper functions to
- create files or folders,
- load files into panda data frames or vise versa,
- save figures into files
(all with suitable standard settings).
"""

from matplotlib.figure import Figure
import pandas as pd
import os as os
from pathlib import Path
import xarray as xr
import apv
from apv.settings.simulation import Simulation as Simsettings
from apv.settings.apv_systems import Default as SystSettings
path_main = apv.settings.user_paths.root


def clear_folder_content(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        os.unlink(file_path)
    print(f'cleared {folder_path}')
    return


def make_dirs_if_not_there(folder_paths: str or list):
    """Checks if the folder/s exist and makes it/them
    if they are not there yet.

    Args:
        folder_paths (str or list of strings)
    """
    # unify Arg to list type
    if type(folder_paths) != list:
        folder_paths = [folder_paths]

    # check all and evt. make
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print('Made folder: ' + str(folder_path))
    return


def df_from_file_or_folder(
        f_path: Path,
        skiprows=0, index_col=None,
        delimiter='\t|,|;', squeeze=False,
        append_all_in_folder=False,
        names=None, header='infer', print_reading_messages=True,
        add_source_file_name_to_df=False):
    '''
    rel_path: relative file path with file extension,
    in case of append_all_in_folder=True: rel_path = folder path
    and file extrionsion doesnt matter

    header=none if no header labels are there
    '''
    df = pd.DataFrame()

    def read_file(f_path):
        if print_reading_messages:
            print('reading ' + str(f_path).split('\\')[-1])
        df = pd.read_csv(
            f_path,
            skiprows=skiprows,
            delimiter=delimiter,
            index_col=index_col,
            names=names,
            header=header,
            engine='python',
            squeeze=squeeze)
        if add_source_file_name_to_df:
            df['source'] = str(f_path).split('\\')[-1]
        return df

    if append_all_in_folder:
        source_files = []
        for file_name in os.listdir(f_path):
            source_files += [os.path.join(f_path, file_name)]
        # generator (as list comprehension but without storing the actual
        # content, only what to loop, which is much faster)
        dfs = (
            read_file(source_file) for source_file in source_files
        )
        df = pd.concat(dfs)
    else:
        try:
            df = read_file(f_path)
        except FileNotFoundError:
            parent_folder_path = "/".join(str(f_path).split("\\")[:-1])
            if os.path.exists(parent_folder_path):
                print(
                    "check path or filename\n" + str(
                        os.listdir(parent_folder_path)))
    return df


def df_from_nc(file_path: str) -> pd.DataFrame:
    """loads a .nc file into a pandas data frame.

    Args:
        file_path (str): relative file path with extension

    Returns:
        pd.DataFrame: [description]
    """

    ds = xr.open_dataset(file_path)
    return ds.to_dataframe()


def df_export(
        df: pd.DataFrame,
        file_name: str,
        rel_path='',
        float_format='%1.3e',
        sep='\t',
        index=True,
        header=True
) -> None:
    '''
    header: to rename columns provide a list of strings here
    float_formats = '%1.2e' for scientific, '%1.2f for float with
    2 after comma digits'
    '''
    desti_path = os.path.join(path_main, rel_path)
    make_dirs_if_not_there(desti_path)
    file_path = os.path.join(desti_path, file_name + '.csv')
    df.to_csv(
        file_path, float_format=float_format,
        index=index, sep=sep, header=header)
    print('exported df to ' + desti_path)
    return


def save_fig(
        fig: Figure,
        file_name: str,
        sub_folder_name='plots',
        parent_folder_path=apv.settings.user_paths.results_folder,
        file_formats=['.jpg'],
        dpi=300,
        transparent=False):
    """Saves a figure with certain default settings into
    results_folder/sub_folder and makes directories if not existing.

    Args:
        fig (matplotlib.figure.Figure): figure to be saved
        file_name (str): file name without extension
        sub_folder_name (str, optional): Defaults to 'plots'.
        parent_folder_path ([type], optional):
        Defaults to apv.settings.user_paths.results_folder.
        file_formats (list, optional): list of formats. Defaults to ['.jpg'].
        dpi (int, optional): Resolution (dots per inch). Defaults to 300.
        transparent (bool, optional): Defaults to False.
    """

    destination_folder = os.path.join(parent_folder_path, sub_folder_name)
    make_dirs_if_not_there(destination_folder)

    for file_format in file_formats:
        file_path = os.path.join(destination_folder, file_name + file_format)
        fig.savefig(file_path, bbox_inches='tight',
                    dpi=dpi, transparent=transparent)
        print('saved fig ' + file_path)
    return


def create_results_folder_path(
        simsettings: Simsettings, APV_SystSettings: SystSettings):

    results_folder_path: Path = apv.settings.user_paths.results_folder / Path(
        simsettings.sim_name,
        APV_SystSettings.module_form
        + f'_res-{simsettings.spatial_resolution}m'
        + f'_step-{simsettings.time_step_in_minutes}min'
        + f'_TMY_aggfunc-{simsettings.TMY_irradiance_aggfunc}'
    )
    return results_folder_path


def get_min_max_of_cols_in_several_csv_files(csv_files: list):

    dfs = (df_from_file_or_folder(file) for file in csv_files)
    df = pd.concat(dfs)

    return df.agg([min, max])
