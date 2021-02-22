##''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 13:21:24 2021

@author: neelpatel
"""

import pandas as pd


#%%

nsrdb_api = '2yxdBVKdOXpp7q7VYLB0XRMdqlhxtCHxlqqd0wnI'


#%%

def retrieve_nsrdb_data(lat, lon, year=2019, interval=15, attributes = 
                        'ghi,dhi,dni,wind_speed,air_temperature,\
surface_albedo')->pd.DataFrame:
    """
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
    api_key = nsrdb_api
    
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
attributes={attr}'.format(year=year, lat=lat, lon=lon, leap=leap_year, 
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


#%%
df = retrieve_nsrdb_data(50.941, 6.367, year=2021, interval=15, attributes = 
                        'ghi,dhi,dni,wind_speed,air_temperature,surface_albedo')
df

##''
import cdsapi
 
c = cdsapi.Client()
 
c.retrieve(
    'reanalysis-uerra-europe-soil-levels',
    {
        'format': 'netcdf',
        'origin': 'uerra_harmonie',
        'variable': 'soil_temperature',
        'soil_level': '2',
        'year': '1968',
        'month': '08',
        'day': '02',
        'time': '06:00',
    },
    'download.nc')

##''

import xarray as xr

ds = xr.open_dataset('download.nc')
df = ds.to_dataframe()

df