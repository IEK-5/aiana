# #
from typing import Literal
import pandas as pd
from datetime import datetime
import pytz
from aiana.settings.sim_settings import SimSettingsDefault


class SimDT:

    sim_dt_naiv: datetime  # and local
    sim_dt_utc: datetime
    sim_dt_str: str
    sim_dt_utc_pd_for_solarposition: pd.Timestamp
    # TODO complete

    start_dt_utc: datetime
    end_dt_utc: datetime

    def __init__(
            self, SimSettings: SimSettingsDefault,
            sim_dt_naiv: datetime = None):

        self.SimSettings = SimSettings
        self.sim_dt_naiv = sim_dt_naiv

        self._set_dt_attributes()

    def update_sim_dt(self, **kwargs):
        """
        year: int = ..., month: int = ..., day: int = ...,
        hour: int = ..., minute: int = ..., as in dt.replace()
        """
        for key in kwargs:
            if key in ['day', 'month', 'year']:
                self.SimSettings.__setattr__(key, kwargs[key])
        self.sim_dt_naiv = self.sim_dt_naiv.replace(**kwargs)
        self._set_dt_attributes()

    def _set_dt_attributes(self):

        start_dt_naiv = self._get_start_or_end_dt_tz_naiv('start')
        end_dt_naiv = self._get_start_or_end_dt_tz_naiv('end')
        if self.sim_dt_naiv is None:
            self.sim_dt_naiv = start_dt_naiv

        self.start_dt_utc: datetime = self._set_dt_to_utc(start_dt_naiv)
        self.end_dt_utc: datetime = self._set_dt_to_utc(end_dt_naiv)
        self.sim_dt_utc: datetime = self._set_dt_to_utc(self.sim_dt_naiv)

        self.sim_dt_utc_pd_for_solarposition: pd.Timestamp = \
            self._substract_time_step_in_minutes_divided_by_X(
                pd.to_datetime(self.sim_dt_utc))

        self.start_dt_str: str = self._get_str_format(dtObj=start_dt_naiv)
        self.sim_dt_str: str = self._get_str_format(dtObj=self.sim_dt_naiv)
        self.end_dt_str: str = self._get_str_format(dtObj=end_dt_naiv)

        self.sunpos_locTime_str: str = \
            self._substract_time_step_in_minutes_divided_by_X(
                pd.to_datetime(self.sim_dt_naiv)).strftime('%H:%M')
        self.irradiance_mean_timeSpan_start_str: str = \
            self._substract_time_step_in_minutes_divided_by_X(
                pd.to_datetime(self.sim_dt_naiv), X=1).strftime('%H:%M')

    def _get_str_format(self, dtObj: datetime) -> str:
        sim_dt_str: str = dtObj.strftime('-%m-%d %H:%M')
        if self.SimSettings.year == 'TMY':
            sim_dt_str = 'TMY'+sim_dt_str
        else:
            sim_dt_str = str(self.SimSettings.year)+sim_dt_str
        return sim_dt_str

    def _get_start_or_end_dt_tz_naiv(
            self, which: Literal['start', 'current', 'end']) -> datetime:

        if self.SimSettings.year == 'TMY':
            year = 2019  # (dummy, non leap year, wont be used)
        else:
            year = self.SimSettings.year

        if which == 'start':
            i = 0
            minute = 0
        elif which == 'end':
            i = -1
            minute = 60-self.SimSettings.time_step_in_minutes

        dt_naiv = datetime(
            year, self.SimSettings.month, self.SimSettings.day,
            self.SimSettings.hours[i], minute)
        return dt_naiv

    def _set_dt_to_utc(self, sim_dt_tz_naiv: datetime) -> datetime:
        pytz_tz = pytz.timezone(self.SimSettings.apv_location.tz)
        self.sim_dt_local: datetime = pytz_tz.localize(sim_dt_tz_naiv)

        sim_dt_utc = self.sim_dt_local.astimezone(pytz.utc)
        return sim_dt_utc

    def _substract_time_step_in_minutes_divided_by_X(
            self, dt_pd: pd.Timestamp, X=2) -> pd.Timestamp:
        timedelta_sec = str(int(60*self.SimSettings.time_step_in_minutes/X))
        return dt_pd-pd.Timedelta(f'{timedelta_sec}sec')


if __name__ == '__main__':
    simSettings = SimSettingsDefault()
    test_simDT = SimDT(simSettings)
    test_simDT.update_sim_dt(hour=10)
    print('custom string:', test_simDT.sim_dt_str)
    print('naiv:', test_simDT.sim_dt_naiv)
    print('local:', test_simDT.sim_dt_local)
    print('UTC:', test_simDT.sim_dt_utc)

# #
