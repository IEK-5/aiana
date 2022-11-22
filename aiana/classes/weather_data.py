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
# #
import pandas as pd
import pvlib
import cdsapi
import pathlib
import os
import yaml
import urllib3
from pathlib import Path
import numpy as np

from aiana.classes.util_classes.settings_handler import Settings
import aiana.utils.files_interface as fi


# suppress InsecureRequestWarning when calling cdsapi retrieve function
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WeatherData:
    """credentials (dict): output of .load_credentials()
    # TODO make class init fast
    """
    ghi: float
    ghi_clearsky: float
    dhi: float
    dni: float
    sunalt: float
    sunaz: float
    dailyCumulated_ghi: float
    dailyCumulated_ghi_clearsky: float

    def __init__(self, settings: Settings, debug_mode=False):
        self.settings = settings
        self.debug_mode = debug_mode

        self.credentials = self.load_API_credentials()

        self.set_self_variables()

        if self.settings.sim.year == 'TMY':
            # sim year is set to dummy non leap year 2019,
            # but with irradiance values averaged

            self.df_irr = self.df_irradiance_to_TMY()
        else:
            self.df_irr = self.load_and_process_insolation_data()

        # make TMY typcal day per month data (W/m2)
        # #multi-index (month, hour...)
        self.df_irradiance_typ_day_per_month = \
            self.calc_typical_day_of_month(self.df_irr)

        # set irradiance and sunpos
        self.set_dhi_dni_ghi_and_sunpos_to_simDT()

        self.calc_cumulative_ghi()

        # dfs:
        # as downloaded from ads,
        # obs_end labeled
        #
        # tmy (braucht leap year filter)
        # typical day per month (braucht leap year filter nicht,
        # geht aber schneller, wenn tmy als input genommen wird)
        # x,y für gencumsky
        # x,y für die klasse für ghi, dhi at simDT

    def set_self_variables(self):

        self.tmy_column_names: list = [
            'ghi_Wm-2', 'ghi_Whm-2',
            'dhi_Wm-2', 'dhi_Whm-2',
            'dni_Wm-2', 'dni_Whm-2',
            'ghi_clearSky_Wm-2', 'ghi_clearSky_Whm-2'
        ]
        # download data for longest full year time span available
        self.download_file_path = self.download_insolation_data(
            self.settings.sim.apv_location,
            '2005-01-01/2022-01-01',
            1  # always 1 minute, will be resampled coarser later
        )

        # resampled ppdata file path
        self.time_step = self.settings.sim.time_step_in_minutes
        self.fn_resampled = str(self.download_file_path).split(
            '\\')[-1].replace('1minute', f'{self.time_step}minute')
        self.resampled_insolation_data_path = \
            self.settings._paths.weatherData_folder / Path(self.fn_resampled)

    def set_dhi_dni_ghi_and_sunpos_to_simDT(self, settings: Settings = None):
        """allow simDT input for fast GHI filter from outside"""
        if settings is None:
            settings = self.settings
        t_stamp = settings._dt.sim_dt_utc
        if settings.sim.use_typDay_perMonth_for_irradianceCalculation:
            s: pd.Series = self.df_irradiance_typ_day_per_month.loc[
                (t_stamp.month, t_stamp.hour, t_stamp.minute)]
        else:
            s: pd.Series = self.df_irr.loc[t_stamp]
        try:
            self.ghi = s['ghi_Wm-2']
            self.dhi = s['dhi_Wm-2']
            self.dni = s['dni_Wm-2']
            self.ghi_clearsky = s['ghi_clearSky_Wm-2']
        except KeyError:
            raise Exception('\n Please choose a simlation time and timestep, which '
                            'can meet, starting at 00:00. E.g. not 15:30 and 60 min\n'
                            )
        # taking sun position in between adjacent right labled irradiation data

        solpos: pd.DataFrame = \
            settings.sim.apv_location.get_solarposition(
                times=settings._dt.sim_dt_utc_pd_for_solarposition,
                temperature=12  # TODO use temperature from ERA5 data
            )
        self.sunalt = float(solpos["elevation"])
        self.sunaz = float(solpos["azimuth"]-180.0)

    def calc_cumulative_ghi(self):
        "for ghi filter and shadow_depth calculation"
        if self.settings.sim.use_typDay_perMonth_for_irradianceCalculation:
            # summing all simulated months and hours (and minutes)
            df_sum = self.df_irradiance_typ_day_per_month.loc[
                pd.IndexSlice[[self.settings.sim.month],
                              self.settings.sim.hours], ].sum()
        else:
            df_sum = self.df_irr.loc[
                self.settings._dt.start_dt_utc: self.settings._dt.end_dt_utc,
                # +1 is not needed for inclusive end with .loc,
                # only with .iloc
            ].sum()

        # daily Cumulated for all hours given in list: settings.sim.hours
        self.dailyCumulated_ghi = df_sum['ghi_Whm-2']
        self.dailyCumulated_ghi_clearsky = df_sum['ghi_clearSky_Whm-2']

    # ## DOWNLOADS ##################

    def load_API_credentials(self) -> dict:
        """loads the credentials from file or prints a guide if file not found

        Args:
            data_store_kind (str): "cds" or "ads"

        Returns:
            [dict]: dictionary with the credentials
        """

        credentials_path = os.path.join(
            pathlib.Path.home(), 'API_credentials.txt')
        try:
            with open(credentials_path, 'r') as f:
                credentials = yaml.safe_load(f)
            return credentials
        except FileNotFoundError:
            print(
                """\n\n
                ##########################################################
                Error: credential-file not found.
                \n
                To get insolation data you need to register at
                https://ads.atmosphere.copernicus.eu
                and to get climate data you need to register at
                https://cds.climate.copernicus.eu.
                After accepting conditions, you can see your UserIDs
                and API Keys in your user profiles in the web pages,
                which you need to enter into the API_credentials.txt file,
                after copying it from the main folder of this repository
                to the home directory of your PC.
                \n
                ##########################################################
                """
            )
            os._exit(1)

    def download_wind_and_T_data(
            self,
            file_name: str,
            location: pvlib.location,
            year: str or list,
            month: str or list,
            day: str or list) -> None:
        '''
        Downloads wind and temperature data from the climate data store (CDS).
        The data set is called "ERA5", which stands for 5th ECMWF Reanalysis
        with ECMWF = European Centre for Medium-Range Weather Forecasts.
        https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=overview
        Time step = 1h, full days
        The download folder is defined in the user_settings.py.

        Args:
           credentials (dict): output of .load_credentials()
           file_name (str): name of the .nc file containing the downloaded data
           location (pvlib.location): pvlib location object to pass coordinates
           year (str or list of str): e.g. '2020' or ['2020', '2021']
           month (str or list of str)
           day (str or list of str)
        '''

        # instance of cdsapi for cds data only
        c = cdsapi.Client(
            url=self.credentials['cds_url'],
            key=self.credentials['cds_key'])
        c.retrieve(
            'reanalysis-era5-land',
            {
                'product_type': 'reanalysis',
                'format': 'netcdf',
                'time': [
                    '00:00', '01:00', '02:00',
                    '03:00', '04:00', '05:00',
                    '06:00', '07:00', '08:00',
                    '09:00', '10:00', '11:00',
                    '12:00', '13:00', '14:00',
                    '15:00', '16:00', '17:00',
                    '18:00', '19:00', '20:00',
                    '21:00', '22:00', '23:00',
                ],
                'area': [
                    location.latitude+0.05,
                    location.longitude-0.05,
                    location.latitude-0.05,
                    location.longitude+0.05
                ],
                'year': year,
                'month': month,
                'day': day,
                'variable': [
                    '10m_u_component_of_wind',
                    '10m_v_component_of_wind',
                    '2m_temperature',
                    'skin_temperature'  # temperature on the surface
                ],
            },
            os.path.join(
                self.settings._paths.weatherData_folder, 'raw_downloads', file_name+'.nc')
        )

    def download_insolation_data(
            self,
            location: pvlib.location.Location,
            date_range: str,
            time_step_in_minutes: int
    ) -> str:
        '''
        Downloads insolation data from the atmosphere data store (ADS), which
        is provided by the Copernicus Atmosphere Monitoring Service (CAMS):
        https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-solar-radiation-timeseries?tab=overview

        The data is satelite based and takes into account the observed weather.
        The download folder is defined in the user_settings.py.

        Args:
            file_name (str): name of the .csv file containing the downloaded
            data location (pvlib.location.Location): location object to pass
            coordinates date_range (str): start and end date str, e.g.
            '2015-01-01/2015-01-02' time_step_in_minutes (int): e.g. 15 results
            in DHI [Wh/m²] within 15 minutes observation periods.
            Has to be 1, 15 or 60.
        Returns:
            file_path (str): file path of the result file

        '''
        if time_step_in_minutes == 60:
            time_step_str = '1hour'
        else:
            time_step_str = f'{time_step_in_minutes}minute'

        file_name = ('insolation-data_' + date_range.replace('/', '_to_') +
                     f'_lat-{location.latitude}'
                     f'_lon-{location.longitude}'
                     f'_time_step-{time_step_str}')

        file_path: Path = self.settings._paths.weatherData_folder/Path(
            'raw_downloads', file_name+'.csv')

        if file_path.exists() is False:
            os.makedirs(file_path.parent)
            print(f'Downloading Insolation data to {file_path}')

            c = cdsapi.Client(
                url=self.credentials['ads_url'],
                key=self.credentials['ads_key'])
            c.retrieve(
                'cams-solar-radiation-timeseries',
                {
                    'sky_type': 'observed_cloud',
                    'location': {
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                    },
                    'altitude': str(location.altitude),
                    'date': date_range,
                    'time_step': time_step_str,
                    'time_reference': 'universal_time',
                    'format': 'csv',
                },
                file_path
            )

        return file_path

    # DATA PROCESSING
    def wind_and_T_data_to_TMY(self, source_file_path):
        return

    def load_and_process_insolation_data(self) -> pd.DataFrame:
        """
        ! will only re-calculate if file does not exist already or
        debug_mode=True !

        - set index to observation end
        - add global and diffusive horizontal irradiance in W/m²
        - add Month, Day... columns to use pivot_table() later

        keeping "right-labeled" instead of "center labeld",
        since lowest resolution of 15 minutes should not
        be made coarser by grouping two adjacent data points

        ...
        """
        # check if already there:
        if self.resampled_insolation_data_path.exists()\
                and not self.debug_mode:
            df = fi.df_from_file_or_folder(
                self.resampled_insolation_data_path, delimiter=' ', index_col=0
            )
            df.set_index(
                pd.to_datetime(df.index, utc=True),  # "right-labeled" as inBR
                inplace=True
            )
            df.Name = self.fn_resampled
            return df

        # else:
        print(f'reading {self.download_file_path}...')
        df: pd.DataFrame = pd.read_csv(
            self.download_file_path, skiprows=42, sep=';')

        df.drop(columns=['TOA', 'Reliability'], inplace=True)

        df[['obs_start', 'obs_end']] = df.iloc[:, 0].str.split(
            '/', 1, expand=True)

        df.set_index(
            pd.to_datetime(df['obs_end'], utc=True),  # "right-labeled" as inBR
            inplace=True
        )

        if self.time_step > 1:
            # downsample_1min_insolation_data
            print(f'coarsening time resolution from 1 '
                  f'to {self.time_step} minutes.')
            df = df.resample(
                f'{self.time_step}min',
                closed='right',
                label='right',
                kind='timestamp'
            ).sum()

        # GHI and DHI are in Wh/m²
        time_step_in_hours = self.time_step/60
        df.loc[:, 'ghi_Wm-2'] = df['GHI']/time_step_in_hours
        df.loc[:, 'dhi_Wm-2'] = df['DHI']/time_step_in_hours
        df.loc[:, 'dni_Wm-2'] = df['BHI']/time_step_in_hours
        df.loc[:, 'ghi_clearSky_Wm-2'] = df['Clear sky GHI']/time_step_in_hours

        # not enough RAM for this test:
        # df.loc[:, 'dni_calced_Wm-2'] = pvlib.irradiance.dni(
        #     df.loc[:, 'ghi_Wm-2'], df.loc[:, 'dhi_Wm-2'],
        #     self.settings.sim.apv_location.get_solarposition(
        #         times=df.index)
        # )

        df.rename(columns={'GHI': 'ghi_Whm-2',
                           'DHI': 'dhi_Whm-2',
                           'BHI': 'dni_Whm-2',
                           'Clear sky GHI': 'ghi_clearSky_Whm-2'
                           },
                  inplace=True)

        # this values are a power per area at the end of the observation period

        df.to_csv(self.resampled_insolation_data_path, sep=' ',
                  columns=self.tmy_column_names)
        df.Name = self.fn_resampled
        return df

    def df_irradiance_to_TMY(self):

        aggfunc = self.settings.sim.TMY_irradiance_aggfunc
        df_tmy_name: str = f'TMY_{aggfunc}_{self.fn_resampled}'
        tmy_file_path = self.settings._paths.weatherData_folder \
            / Path(df_tmy_name)

        if tmy_file_path.exists() and not self.debug_mode:
            df_tmy = fi.df_from_file_or_folder(
                tmy_file_path, delimiter=' ', index_col=0)
            df_tmy.set_index(
                pd.to_datetime(df_tmy.index, utc=True), inplace=True)
        else:
            df = self.load_and_process_insolation_data()
            # filter out 29th Feb
            mask = (df.index.is_leap_year) & (df.index.dayofyear == 60)
            df.loc[:] = df[~mask]
            # .loc[:] prevents creating new df object, which would loose .Name

            df.loc[:, 'month'] = df.index.month
            df.loc[:, 'day'] = df.index.day
            df.loc[:, 'hour'] = df.index.hour
            df.loc[:, 'minute'] = df.index.minute

            df_tmy = pd.pivot_table(
                df,
                index=['month', 'day', 'hour', 'minute'],
                values=self.tmy_column_names,
                aggfunc=self.settings.sim.TMY_irradiance_aggfunc)

            freq = f"{self.settings.sim.time_step_in_minutes}min"
            df_tmy.index = pd.date_range(
                start="2019-01-01", periods=len(df_tmy), freq=freq, tz='utc')

            df_tmy.to_csv(tmy_file_path, sep=' ')

        df_tmy.Name = df_tmy_name
        return df_tmy

    def calc_typical_day_of_month(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        df is meant for self.df_irradiance_tmy

        Extract from TMY irradiation data 3 typical representative days
        of each month: day 1 is when daily GHI itegral is minimum, day 2 is
        when daily GHI integral is maximum, and day 3 is the day that is most
        close to the daily average GHI of the month.

        Returns:
            [df_all]: [DataFrame with values and indexes of the 3 days of
                       each month]
        """

        df.loc[:, 'month'] = df.index.month
        df.loc[:, 'hour'] = df.index.hour
        df.loc[:, 'minute'] = df.index.minute

        df_typ_day_per_month = pd.pivot_table(
            df,
            index=['month', 'hour', 'minute'],  # no day ->all days are grouped
            values=self.tmy_column_names,
            aggfunc='mean')  # mean from the TMY made
        # itself with aggfunc min or mean or max

        return df_typ_day_per_month

        ##############
        # backup code for a min or max day of a certain month:

        # create TMY from ADS yearly data
        df_tmy = pd.pivot_table(df,
                                index=['month', 'day', 'hour'],
                                values=['GHI', 'DHI'], aggfunc=np.mean)

        # create daily sum to identify max, min, and avg
        df_day_sums = pd.pivot_table(
            df,
            index=['month', 'day'],
            values=['GHI'],
            aggfunc='sum')
        # identify value where sum is max, min, or avg
        df_all = pd.pivot_table(
            df_day_sums, index='month',
            values=['GHI'], aggfunc=['min', 'mean', 'max'])
        # give index where max, min, and avg idenitified
        for month in range(1, 13):
            df_all.loc[month, 'day_min'] = np.argmin(df_day_sums.loc[month])+1
            df_all.loc[month, 'day_max'] = np.argmax(df_day_sums.loc[month])+1
            df_all.loc[month, 'day_nearest_to_mean'] = np.argmin(
                abs(df_day_sums.loc[month]-df_all.loc[month, 'mean']))+1

        return df_tmy, df_all


# if __name__ == '__main__':
