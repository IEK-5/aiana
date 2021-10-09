import pandas as pd
from collections import namedtuple
import apv
from apv.utils import units_converter
from pathlib import Path

RMSE_MBE_results = namedtuple(
    'RMSE_MBE_results', ('mbe', 'rel_mbe', 'rmse', 'rel_rmse'))


def merge_hours_to_day(csv_parent_folder, SimSettings, month, hours=[0, 23]):
    df = apv.utils.files_interface.df_from_file_or_folder(
        csv_parent_folder, append_all_in_folder=True, index_col=0)
    df['xy'] = df['x'].astype(str) + df['y'].astype(str)

    df_merged = pd.pivot_table(
        df, index=['x', 'y'], values=['Wm2', 'PARGround'], aggfunc='sum')
    strt = f'{month}-{15}_{hours[0]}:00'
    enddt = f'{month}-{15}_{hours[-1]}:00'
    df_merged = units_converter.irradiance_to_shadowdepth(
        df=df_merged, SimSettings=SimSettings, strt=strt, enddt=enddt)
    csv_file_path = csv_parent_folder / Path(
        'radiation' + '_cumulative_' + str(month) + '.csv')
    df_merged.to_csv(csv_file_path)
    print(f'Typical day cumulative hours of month {month} completed!\n',
          'NOTE: Shadow_depth was recalculated for cumulative data\n')
    return df_merged


def calc_RMSE_MBE(arr1: pd.Series, arr2: pd.Series) -> namedtuple:
    """calculates root mean square error (RMSE) and mean bias error (MBE)
    between two series arr1 and arr2.
    note: substracting two series happens via the index values not via their
    position (via "loc" not via "iloc").
    """

    mbe = (arr2 - arr1).mean()
    rmse = ((arr1 - arr2)**2).mean()**0.5
    max_all = max(arr1.max(), arr2.max())
    min_all = min(arr1.min(), arr2.min())
    rel_mbe = mbe / ((max_all - min_all)/2)
    rel_rmse = rmse / ((max_all - min_all)/2)

    return RMSE_MBE_results(mbe, rel_mbe, rmse, rel_rmse)


def calc_RMSE_MBE_old(arr1: pd.Series, arr2: pd.Series) -> pd.DataFrame:
    """calculates root mean square error (RMSE) and mean bias error (MBE)
    between two series arr1 and arr2.
    note: substracting two series works via the index values not their
    position (via "loc" not via "iloc").
    """

    df_meta = pd.DataFrame()

    if arr1.name == arr2.name:
        label = arr1.name
    else:
        label = arr1.name+' vs '+arr2.name

    df_meta.loc['RMSE', label] = (
        (arr1 - arr2)**2).mean()**0.5

    df_meta.loc['MBE', label] = (
        arr1 - arr2).mean()

    mean_all = (arr1.mean() + arr2.mean())/2
    df_meta.loc['RMSE/mean', label] = df_meta.loc['RMSE', label]/mean_all
    df_meta.loc['MBE/mean', label] = df_meta.loc['MBE', label]/mean_all

    return df_meta
