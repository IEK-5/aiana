import pandas as pd
from datetime import datetime
import pytz
from apv.settings.simulation import Simulation


class SimDT:
    """
    #TODO simulation settings time string hierhin verschieben einmalig
    zum start und dann nur hier drin ändern, damit nicht alle settings
    mit immer übergeben werden müssen, wenn es eigentlich nur die sim zeit ist
    """

    def __init__(self, SimSettings: Simulation):

        self.SimSettings = SimSettings
        self.sim_dt_local: datetime = None
        self.sim_dt_utc: datetime = None
        self.sim_dt_utc_pd: pd.Timestamp = None
        self.startdt_utc: datetime = None
        self.enddt_utc: datetime = None
        self.times: pd.Timestamp = None

        # self.hour_of_tmy_utc: int = None
        # self.start_hour_of_tmy_utc: int = None
        # self.end_hour_of_tmy_utc: int = None

        self.set_time_variables()

    def set_time_variables(self):
        tz = self.SimSettings.apv_location.tz

        self.sim_dt_utc: datetime = self.convert_settings_localtime_to_UTC(
            self.SimSettings.sim_date_time, tz
        )
        self.startdt_utc: datetime = self.convert_settings_localtime_to_UTC(
            self.SimSettings.startdt, tz
        )
        self.enddt_utc: datetime = self.convert_settings_localtime_to_UTC(
            self.SimSettings.enddt, tz
        )

        """
        self.hour_of_tmy_utc: int = self.get_hour_of_tmy(
            self.sim_dt_utc)
        self.start_hour_of_tmy_utc: int = self.get_hour_of_tmy(
            self.startdt_utc)
        self.end_hour_of_tmy_utc: int = self.get_hour_of_tmy(
            self.enddt_utc) """

        self.sim_dt_utc_pd: pd.Timestamp = pd.to_datetime(self.sim_dt_utc)

        self.times = pd.date_range(
            start=self.startdt_utc, end=self.enddt_utc,
            freq=f'{self.SimSettings.time_step_in_minutes}min', closed='right')

    def convert_settings_localtime_to_UTC(
            self, date_time_str: str, tz: str) -> datetime:
        """converts local time string to a utc datetime object

        carefull for later: when replacing 2022 with real year, leap_year has
        to be considered for hour_of_year (if it is still used then)

        Args:
            date_time_str (str): format: 'month-day_hour'+'h',
            e.g.'06-15_10h'

        Returns:
            int: hours_of_year
        """

        if self.SimSettings.sim_year == 'TMY':
            year_str = '2019'  # (dummy, non leap year, wont be used)
        else:
            year_str = str(self.SimSettings.sim_year)

        sim_dt_tz_naiv: datetime = datetime.strptime(
            year_str+'-'+date_time_str, '%Y-%m-%d_%H:%M')
        pytz_tz = pytz.timezone(tz)
        self.sim_dt_local: datetime = pytz_tz.localize(sim_dt_tz_naiv)

        sim_dt_utc = self.sim_dt_local.astimezone(pytz.utc)
        return sim_dt_utc

    """ def get_hour_of_tmy(self, sim_dt_utc: datetime) -> int:
        ""converts str to hours_of_year

        Args:
            date_time_str (str): format: 'month-day_hour'+'h',
            e.g.'06-15_10h'

        Returns:
            int: hours_of_year
        ""

        dt_ref = datetime(sim_dt_utc.year, 1, 1, 0, tzinfo=pytz.utc)
        delta = sim_dt_utc - dt_ref
        hours_of_year = delta.days * 24 + sim_dt_utc.hour
        return hours_of_year """
