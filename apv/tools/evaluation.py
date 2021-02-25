import pandas as pd


def calc_RMSE_MBE(arr1: pd.Series, arr2: pd.Series) -> pd.DataFrame:

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

    return df_meta
