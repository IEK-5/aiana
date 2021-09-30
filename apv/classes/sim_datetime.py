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

        self.startdt_utc: datetime = self.convert_settings_localtime_to_UTC(
            SimSettings.startdt,
            SimSettings.apv_location.tz
        )
        self.enddt_utc: datetime = self.convert_settings_localtime_to_UTC(
            SimSettings.enddt,
            SimSettings.apv_location.tz
        )

        self.times = pd.date_range(start=self.startdt_utc, end=self.enddt_utc,
                                   freq='1h', closed='right')

    def convert_settings_localtime_to_UTC(
            self, date_time_str: str, tz: str) -> datetime:
        """converts str to hours_of_year
        we take year 2022 as year but dont use it at the moment (only use tmy)

        carefull for later: when replacing 2022 with real year, leap_year has
        to be considered for hour_of_year (if it is still used then)

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
