# #
import pandas as pd
# import shutil
import pvlib
import cdsapi
import pathlib
import os
import yaml
import urllib3
from pathlib import Path

import apv

# suppress InsecureRequestWarning when calling cdsapi retrieve function
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_API_credentials() -> dict:
    """loads the credentials from file or prints a guide if file not found

    Args:
        data_store_kind (str): "cds" or "ads"

    Returns:
        [dict]: dictionary with the credentials
    """

    credentials_path = os.path.join(pathlib.Path.home(), 'API_credentials.txt')
    try:
        with open(credentials_path, 'r') as f:
            credentials = yaml.safe_load(f)
        return credentials
    except FileNotFoundError:
        print("""
              ##########################################################
              Error: credential-file not found.
              \n
              To get insolation and climate data you need to register at
              https://ads.atmosphere.copernicus.eu
              and
              https://cds.climate.copernicus.eu,
              respectivly.
              After accepting conditions, you can see your UserIDs
              and API Keys in your user profiles in the web pages,
              which you need to enter into the API_credentials.txt file,
              after copying it from the main folder of this repository
              to your home directory of your PC.
              \n
              ##########################################################
              """
              )


def download_wind_and_T_data(
        credentials: dict,
        file_name: str,
        location: pvlib.location,
        year: str or list,
        month: str or list,
        day: str or list):
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
    c = cdsapi.Client(url=credentials['cds_url'], key=credentials['cds_key'])
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
        os.path.join(apv.settings.UserPaths.data_download_folder, file_name+'.nc')
    )


def download_insolation_data(
        credentials: dict,
        file_name: str,
        location: pvlib.location,
        date_range: str,
        time_step: str):
    '''
    Downloads insolation data from the atmosphere data store (ADS),
    which is provided by the Copernicus Atmosphere Monitoring Service (CAMS):
    https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-solar-radiation-timeseries?tab=overview

    The data is satelite based and takes into account the observed weather.
    The download folder is defined in the user_settings.py.

    Args:
        credentials (dict): output of .load_credentials()
        file_name (str): name of the .csv file containing the downloaded data
        location (pvlib.location): pvlib location object to pass coordinates
        date_range (str): start and end date str, e.g. '2015-01-01/2015-01-02'
        time_step (str): e.g. '15minute' or '1hour'
    '''

    c = cdsapi.Client(url=credentials['ads_url'], key=credentials['ads_key'])
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
            'time_step': time_step,
            'time_reference': 'universal_time',
            'format': 'csv',
        },
        os.path.join(apv.settings.UserPaths.data_download_folder, file_name+'.csv')
    )


def retrieve_nsrdb_data(
        lat, lon, year=2019, interval=15,
        attributes='ghi,dhi,dni,wind_speed,air_temperature,surface_albedo'
) -> pd.DataFrame:
    """
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

    """
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

    return data
