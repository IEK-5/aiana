""" This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>."""

"""This module contains project independent helper functions to
- create files or folders,
- load files into panda data frames or vise versa,
- save figures into files
(all with suitable standard settings).
"""
# #
import xarray as xr
from matplotlib.figure import Figure
import pandas as pd
import os as os
from pathlib import Path


def clear_folder_content(folder_path: str, print_msg=True):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        os.unlink(file_path)
    if print_msg:
        print(f'cleared {folder_path}')


def make_dirs_if_not_there(folder_paths: (str | list)):
    """Checks if the folder/s exist and makes it/them
    if they are not there yet.

    Args:
        folder_paths (str or Path or list of strings/Paths)
    """
    # unify Arg to list type
    if type(folder_paths) != list:
        folder_paths = [folder_paths]

    # check all and evt. make
    for folder_path in folder_paths:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print('Made folder: ' + str(folder_path))


def df_from_file_or_folder(
        f_path: Path,
        skiprows=0, index_col=None,
        delimiter='\t|,|;',
        append_all_in_folder=False,
        names=None, header='infer', print_reading_messages=True,
        add_source_file_name_to_df=False) -> pd.DataFrame:
    '''
    rel_path: relative file path with file extension,
    in case of append_all_in_folder=True: rel_path = folder path
    containing the csv files. Sub folders are ignored.

    header=none if no header labels are there
    '''
    df = pd.DataFrame()

    def read_file(f_path) -> pd.DataFrame:
        if print_reading_messages:
            print('reading ' + str(f_path).split('\\')[-1])
        df = pd.read_csv(
            f_path,
            skiprows=skiprows,
            delimiter=delimiter,
            index_col=index_col,
            names=names,
            header=header,
            engine='python')
        if add_source_file_name_to_df:
            df['source'] = str(f_path).split('\\')[-1]
        return df

    if append_all_in_folder:
        source_files = []
        for file_name in os.listdir(f_path):
            if file_name[-4:] == '.csv':
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
            else:
                raise FileNotFoundError(parent_folder_path)
    return df


def df_from_nc(file_path: str) -> pd.DataFrame:
    """loads a .nc file into a pandas data frame.

    Args:
        file_path (str): relative file path with extension

    Returns:
        pd.DataFrame: [description]
    """

    ds: xr.Dataset = xr.open_dataset(file_path)
    return ds.to_dataframe()


def df_export(
        df: pd.DataFrame,
        csv_file_path,
        float_format='%1.3e',
        sep='\t',
        index=True,
        header=True,
        h5_compression=False
) -> None:
    '''
    saves into .csv file with customized default settings.
    header: to rename columns provide a list of strings here
    float_formats = '%1.2e' for scientific, '%1.2f for float with
    2 after comma digits'
    '''
    if h5_compression:
        df.to_hdf(mode='w')

    df.to_csv(
        csv_file_path, float_format=float_format,
        index=index, sep=sep, header=header)
    print('exported df to', csv_file_path)


def save_fig(
        fig: Figure,
        file_path: Path,
        dpi=300,
        transparent=False):
    """Saves a figure with certain default settings into file_path
    and makes parent directories if not existing.

    Args:
        fig (matplotlib.figure.Figure): figure to be saved
        file_path (Path from pathlib): file path with extension
        dpi (int, optional): Resolution (dots per inch). Defaults to 300.
        transparent (bool, optional): Defaults to False.
    """
    if type(file_path) != Path:
        file_path = Path(file_path)
    make_dirs_if_not_there(file_path.parent)
    fig.savefig(file_path, bbox_inches='tight',
                dpi=dpi, transparent=transparent)
    print('saved fig ' + str(file_path))


def get_min_max_in_several_csv_files(csv_files: list) -> pd.DataFrame:
    """

    Args:
        csv_files (list): list of csv-file-paths (list items: Path)

    Returns:
        pd.DataFrame with min and max of each csv-file-column
    """

    dfs = (df_from_file_or_folder(file) for file in csv_files)
    df = pd.concat(dfs)

    return df.agg([min, max])


def write_to_txt_file(file_path: Path, text: str, mode='w'):
    if type(file_path) != Path:
        file_path = Path(file_path)
    make_dirs_if_not_there(file_path.parent)
    with open(file_path, mode) as f:
        f.writelines(text)
        f.close()
