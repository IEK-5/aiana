import pandas as pd
from datetime import datetime


def get_hour_of_year(date_time_str: str) -> int:
    """converts str to hours_of_year

    Args:
        date_time_str (str): format: 'month-day_hour'+'h',
        e.g.'06-15_10h'

    Returns:
        int: hours_of_year
    """
    date_time_obj = datetime.strptime(date_time_str, '%m-%d_%Hh')

    date_time_str_ref = '01-01_00h'
    date_time_obj_ref = datetime.strptime(date_time_str_ref, '%m-%d_%Hh')

    delta = date_time_obj - date_time_obj_ref
    return delta.days * 24 + date_time_obj.hour


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


intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)


def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])
