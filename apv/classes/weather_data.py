# #
import pandas as pd
from pandas.io.formats.format import TextAdjustment
# import shutil
import pvlib
import cdsapi
import pathlib
import os
from pytz import timezone
import yaml
import urllib3
from pathlib import Path
from typing import Literal
import numpy as np
import apv
import apv.settings.user_paths as user_paths
from pvlib import location
from apv.settings.simulation import Simulation
from apv.classes.sim_datetime import SimDT


# suppress InsecureRequestWarning when calling cdsapi retrieve function
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WeatherData:
    """credentials (dict): output of .load_credentials()
    """

    def __init__(self, SimSettings: Simulation, debug_mode=False):
        self.SimSettings = SimSettings
        self.debug_mode = debug_mode
        self.simDT = SimDT(SimSettings)

        self.credentials = self.load_API_credentials()
        self.ghi: float = None
        self.ghi_clearsky: float = None
        self.dhi: float = None
        self.dni: float = None
        self.sunalt: float = None
        self.sunaz: float = None

        self.set_self_variables()

        if self.SimSettings.sim_year == 'TMY':
            # sim year is set to dummy non leap year 2019,
            # but with irradiance values averaged

            self.df_irr = self.df_irradiance_to_TMY()
            # make TMY typcal day per month data (W/m2)
            # #multi-index (month, hour...)
            self.df_irradiance_typ_day_per_month = \
                self.typical_day_of_month(self.df_irr)
        else:
            self.df_irr = self.load_and_process_insolation_data()

        self.set_dhi_dni_ghi_and_sunpos_to_simDT(self.simDT)
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
            self.SimSettings.apv_location,
            '2005-01-01/2022-01-01',
            1  # always 1 minute, will be resampled coarser later
        )

        # resampled data file path
        self.time_step = self.SimSettings.time_step_in_minutes
        self.fn_resampled = str(self.download_file_path).split(
            '\\')[-1].replace('1minute', f'{self.time_step}minute')
        self.weather_folder_path = user_paths.bifacial_radiance_files_folder \
            / Path('satellite_weatherData')
        self.resampled_insolation_data_path: Path = \
            self.weather_folder_path/self.fn_resampled

    def set_dhi_dni_ghi_and_sunpos_to_simDT(self, simDT: SimDT):

        self.ghi = self.df_irr.loc[simDT.sim_dt_utc, 'ghi_Wm-2']
        self.dhi = self.df_irr.loc[simDT.sim_dt_utc, 'dhi_Wm-2']
        self.dni = self.df_irr.loc[simDT.sim_dt_utc, 'dni_Wm-2']
        self.ghi_clearsky = self.df_irr.loc[
            simDT.sim_dt_utc, 'ghi_clearSky_Wm-2']
        # whereby for sky to untilted ground cos(tilt) = 1 and GHI = DNI + DHI

        # sun position
        # 30 seconds rounding error should not matter for sunposition
        timedelta = str(int(self.SimSettings.time_step_in_minutes/2))
        solpos: pd.DataFrame = \
            self.SimSettings.apv_location.get_solarposition(
                times=simDT.sim_dt_utc_pd-pd.Timedelta(f'{timedelta}min'),
                temperature=12  # TODO use temperature from ERA5 data
            )

        self.sunalt = float(solpos.elevation)
        self.sunaz = float(solpos.azimuth)-180.0

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
            os.path.join(user_paths.data_download_folder, file_name+'.nc')
        )

    def download_insolation_data(
            self,
            location: pvlib.location.Location,
            date_range: str,
            time_step_in_minutes: int
    ) -> str:
        '''
        Downloads insolation data from the atmosphere data store (ADS),
        which is provided by the Copernicus Atmosphere Monitoring Service (CAMS):
        https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-solar-radiation-timeseries?tab=overview

        The data is satelite based and takes into account the observed weather.
        The download folder is defined in the user_settings.py.

        Args:
            file_name (str): name of the .csv file containing the downloaded data
            location (pvlib.location.Location): location object to pass coordinates
            date_range (str): start and end date str, e.g. '2015-01-01/2015-01-02'
            time_step_in_minutes (int): e.g. 15 results in DHI [Wh/m²] within
            15 minutes observation periods. Has to be 1, 15 or 60.
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

        file_path: Path = user_paths.data_download_folder/Path(
            file_name+'.csv')

        if file_path.exists() is False:
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
            df = apv.utils.files_interface.df_from_file_or_folder(
                self.resampled_insolation_data_path, delimiter=' ', index_col=0
            )
            df.set_index(
                pd.to_datetime(df.index, utc=True),  # "right-labeled" as inBR
                inplace=True
            )
            df.Name = self.fn_resampled
            return df

        # else:
        apv.utils.files_interface.make_dirs_if_not_there(
            self.weather_folder_path)
        print(f'reading {self.download_file_path}...')
        df: pd.DataFrame = pd.read_csv(
            self.download_file_path, skiprows=42, sep=';')

        df.drop(columns=['TOA', 'Reliability'], inplace=True)

        df[['obs_start', 'obs_end']] = \
            df.iloc[:, 0].str.split('/', 1, expand=True)

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
        #     self.SimSettings.apv_location.get_solarposition(
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

        aggfunc = self.SimSettings.TMY_irradiance_aggfunc
        df_tmy_name: str = f'TMY_{aggfunc}_{self.fn_resampled}'
        tmy_file_path = user_paths.bifacial_radiance_files_folder / Path(
            'satellite_weatherData', df_tmy_name)

        if tmy_file_path.exists() and not self.debug_mode:
            df_tmy = apv.utils.files_interface.df_from_file_or_folder(
                tmy_file_path, delimiter=' ', index_col=0)
            df_tmy = df_tmy.set_index(pd.to_datetime(df_tmy.index, utc=True))
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
                aggfunc=self.SimSettings.TMY_irradiance_aggfunc)

            freq = f"{self.SimSettings.time_step_in_minutes}min"
            df_tmy.index = pd.date_range(
                start="2019-01-01", periods=len(df_tmy), freq=freq, tz='utc')

            df_tmy.to_csv(tmy_file_path, sep=' ')

        df_tmy.Name = df_tmy_name
        return df_tmy

    """
    def write_ghi_dhi_data_for_gendaylit():

        # else:
        apv.utils.files_interface.make_dirs_if_not_there(tmy_folder_path)

        # create average GHI and DHI for each hour per year
        group_list = [df.index.month, df.index.day, df.index.hour]
        x = df['GHI'].groupby(group_list).mean()
        y = df['DHI'].groupby(group_list).mean()
        x = x.reset_index(drop=True)
        y = y.reset_index(drop=True)

        tmy_data = pd.DataFrame({'ghi': x, 'dhi': y})
        tmy_data.to_csv(tmy_file_path, index=False, header=False, sep=' ',
                        columns=['ghi', 'dhi']  # to be sure about order
                        )
        return tmy_data
        # split time stamp for pivot

        df['Month'] = df.index.month
        df['Day'] = df.index.day
        df['Hour'] = df.index.hour
        df['Minute'] = df.index.minute

        df_tmy = pd.pivot_table(
            df,
            index=['Month', 'Day', 'Hour'],
            values=['GHI', 'DHI'])

        return df_tmy """

    def typical_day_of_month(self, df):
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


"""


def retrieve_nsrdb_data(
        lat, lon, year=2019, interval=15,
        attributes='ghi,dhi,dni,wind_speed,air_temperature,surface_albedo'
) -> pd.DataFrame:
    \"""
    by Neel Patel

    Parameters
    ----------
    lat : latitude of location
    lon : longitude of location
    year : year for which data is to be retrieved [possible: 2017, 2018, 2019]
    interval : temporal resolution of the data in minutes[possible: 15, 30, 60]
    attributes : weather data parameters required.
                 The default is
                 'ghi,dhi,dni,wind_speed,air_temperature,surface_albedo'.

    Returns
    -------
    data : df containing requested weather attributes with UTC timestamps.

    \"""
    api_key = '2yxdBVKdOXpp7q7VYLB0XRMdqlhxtCHxlqqd0wnI'
    # true will return leap day data if present, false will not
    leap_year = 'true'
    # true will use UTC, false will use the local time zone of the data.
    utc = 'false'
    your_name = 'does+not+matter'
    reason_for_use = 'does+not+matter'
    your_affiliation = 'does+not+matter'
    your_email = 'usermail@usermail.com'
    mailing_list = 'false'

    # url to get nsrdb data for europe
    url_europe = 'https://developer.nrel.gov/api/nsrdb/v2/solar/msg-iodc-\
    download.csv?wkt=POINT({lon}%20{lat})&names={year}&leap_day={leap}&\
    interval={interval}&utc={utc}&full_name={name}&email={email}&affiliation=\
    {affiliation}&mailing_list={mailing_list}&reason={reason}&api_key={api}&\
    attributes={attr}'.format(
        year=year, lat=lat, lon=lon, leap=leap_year,
        interval=interval, utc=utc, name=your_name,
        email=your_email, mailing_list=mailing_list,
        affiliation=your_affiliation, api=api_key,
        reason=reason_for_use, attr=attributes)

    data = pd.read_csv(url_europe, skiprows=2)

    # set index
    data = data.set_index(pd.date_range('1/1/{yr}'.format(yr=year),
                                        freq=str(interval) + 'Min',
                                        periods=525600 / interval))

    return data """

# #
if __name__ == '__main__':
    SimSettings = apv.settings.simulation.Simulation()
    # SimSettings.time_step_in_minutes = 1
    WData = WeatherData(SimSettings,  # debug_mode=True
                        )
    # #
    df = WData.df_irradiance_typ_day_per_month
    month = int(SimSettings.sim_date_time.split('-')[0])
    df.loc[(1), 'ghi_Whm-2'].sum()
    # #
    from typing import Literal
    Test: 1 or 2 = 2
    type(Test)
    Test
    # #
    df.loc[simDT.sim_dt_utc]
    # #
    df.Name
    # #
    df['time'] = df.day + df.hour

    df

    # #
    WData.set_dhi_dni_ghi_and_sunpos_to_simDT(simDT)
    WData.dhi
    # #

    sim_dt_tz_naiv: datetime = datetime.strptime(
        year_str+'-'+date_time_str, '%y-%m-%d_%H:%M')
    pytz_tz = pytz.timezone(tz)
    self.sim_dt_local: datetime = pytz_tz.localize(sim_dt_tz_naiv)

    sim_dt_utc = self.sim_dt_local.astimezone(pytz.utc)
    # #

    group_list = [df.index.month, df.index.day, df.index.hour, df.index.minute]

    df2 = df.groupby(group_list).mean()
    df2
    # #
    df
    # #
    test = pd.DataFrame(columns=['a'])

    # test.Name = 'hi'
    test['a'] = 2
    test.Name
    # test
