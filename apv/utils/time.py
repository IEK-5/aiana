# #
import pandas as pd
from datetime import datetime
import pytz
from apv.settings.simulation import Simulation


class SimDT:
    """
    """

    def __init__(self, SimSettings: Simulation):

        self.sim_dt_utc: datetime = self.convert_settings_localtime_to_UTC(
            SimSettings.sim_date_time,
            SimSettings.apv_location.tz
        )

        self.sim_dt_utc_pd: pd.Timestamp = pd.to_datetime(self.sim_dt_utc)

        self.hour_of_tmy: int = self.get_hour_of_tmy(self.sim_dt_utc)

    def convert_settings_localtime_to_UTC(
            self, date_time_str: str, tz: str) -> datetime:
        """converts str to hours_of_year
        we take year 2022 as year but dont use it at the moment (only use tmy)

        carefull for later: when replacing 2022 with real year, leap_year has to
        be considered for hour_of_year (if it is still used then)

        Args:
            date_time_str (str): format: 'month-day_hour'+'h',
            e.g.'06-15_10h'

        Returns:
            int: hours_of_year
        """
        sim_dt_tz_naiv: datetime = datetime.strptime(
            '22-'+date_time_str, '%y-%m-%d_%Hh')
        pytz_tz = pytz.timezone(tz)
        sim_dt = pytz_tz.localize(sim_dt_tz_naiv)

        sim_dt_utc = sim_dt.astimezone(pytz.utc)
        return sim_dt_utc

    def get_hour_of_tmy(self, sim_dt_utc: datetime) -> int:
        """converts str to hours_of_year

        Args:
            date_time_str (str): format: 'month-day_hour'+'h',
            e.g.'06-15_10h'

        Returns:
            int: hours_of_year
        """

        dt_ref = datetime(sim_dt_utc.year, 1, 1, 0, tzinfo=pytz.utc)
        delta = sim_dt_utc - dt_ref
        hours_of_year = delta.days * 24 + sim_dt_utc.hour
        return hours_of_year


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


# #
if __name__ == '__main__':
    import apv
    SimSettings = apv.settings.simulation.Simulation()
    SimSettings.sim_date_time = '01-01_0h'
    sim_dt_utc = convert_settings_localtime_to_UTC(
        SimSettings.sim_date_time, SimSettings.apv_location.tz)
    print(get_hour_of_year(sim_dt_utc))
