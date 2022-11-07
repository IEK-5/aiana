# #
import pandas as pd


def column_to_utc_index(
        df: pd.DataFrame,
        timestamp_column_header: str,
        source_timezone: str
) -> pd.DataFrame:
    """converts a date-time column into a pd.timestamp, takes the result
    as index and converts it from the given source timezone to utc

    Args:
        df (pd.DataFrame): Dataframe to be modified
        timestamp_column_header (str): source column name
        source_timezone (str): e.g. 'Etc/GMT+1' for Germany
    """

    df = df.set_index(pd.to_datetime(df[timestamp_column_header]))
    df.index = df.index.tz_localize(source_timezone).tz_convert('UTC')
    df.index.names = ['time_utc']

    return df


def add_missing_timestamp_indices(df: pd.DataFrame) -> pd.DataFrame:
    # get timedelta between first two rows:
    time_delta_min_str = str(int(
        (df.index[1]-df.index[0]).total_seconds()/60))+'min'
    df_complete = df.resample(time_delta_min_str).mean()
    print(
        str(len(df)-len(df_complete))
        + ' row(s) were missing and have been added.')

    return df_complete
