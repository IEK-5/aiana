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
from apv.settings import UserPaths as UserPaths
path_main = apv.settings.UserPaths.root


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
        rel_path: Path, path_main=path_main,
        skiprows=0, index_col=None,
        delimiter='\t|,|;', squeeze=False,
        append_all_in_folder=False,
        names=None, header='infer', print_reading_messages=True):
    '''
    rel_path: relative file path with file extension,
    in case of append_all_in_folder=True: rel_path = folder path
    and file extrionsion doesnt matter

    header=none if no header labels are there
    '''
    df = pd.DataFrame()

    def read_file(source_file):
        if print_reading_messages:
            print('reading ' + source_file.split('\\')[-1])
        return pd.read_csv(
            source_file,
            skiprows=skiprows,
            delimiter=delimiter,
            index_col=index_col,
            names=names,
            header=header,
            engine='python',
            squeeze=squeeze)

    if append_all_in_folder:
        source_folder = os.path.join(path_main, rel_path)
        source_files = []
        for file_name in os.listdir(source_folder):
            source_files += [os.path.join(path_main, rel_path, file_name)]
        # generator (as list comprehension but without storing the actual
        # content, only what to loop, which is much faster)
        dfs = (
            read_file(source_file) for source_file in source_files
        )
        df = pd.concat(dfs)
    else:
        source_file = os.path.join(path_main, rel_path)
        try:
            df = read_file(source_file)
        except FileNotFoundError:
            folder_path = "/".join(source_file.split("\\")[:-1])
            if os.path.exists(folder_path):
                print("check filename: " + str(os.listdir(folder_path)))
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
        parent_folder_path=apv.settings.UserPaths.results_folder,
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
        Defaults to apv.settings.UserPaths.results_folder.
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
