import pandas as pd
from collections import namedtuple

RMSE_MBE_results = namedtuple(
    'RMSE_MBE_results', ('mbe', 'rel_mbe', 'rmse', 'rel_rmse'))


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
