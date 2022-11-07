# #
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 14:34:30 2021

@author: neelpatel
adapted and modified by Leonard Raumann, June 2021
"""

import cdsapi
import yaml
import os
import pathlib
import pygrib
import math
import numpy as np
from scipy.constants import convert_temperature
from scipy.interpolate import interp1d
import pandas as pd
import urllib3

# suppress InsecureRequestWarning when calling cdsapi retrieve function
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#%% get credentials for era5
# put keys in the .vipvkeys file 
# create and store this file in your home directory
import pathlib
vipvkeys_path = os.path.join(pathlib.Path.home(), '.vipvkeys')
with open(vipvkeys_path, 'r') as f:
    vipvkeys = yaml.safe_load(f)


#%% function to retrieve temperature and wind data for a box from ERA5

def retrieve_era5_boundingboxdata(lat_max, lat_min, lon_max, lon_min, 
                                  year, month, day):
    """
    Retrieve temperature and wind data for a bounding box in grib format.
    
    Parameters
    ----------
    lat_max : float
        DESCRIPTION.
    lat_min : float
        DESCRIPTION.
    lon_max : float
        DESCRIPTION.
    lon_min : float
        DESCRIPTION.
    year : int
        DESCRIPTION.
    month : int
        DESCRIPTION.
    day : int
        DESCRIPTION.

    Returns
    -------
    era5_file_location : str
        Location of the downloaded file.
    """
    # instance of cdsapi for cds data only
    c = cdsapi.Client(url=vipvkeys['era5_url'], key=vipvkeys['era5_key'])
    
    # bounding_box lat/lon order: [lat_max, lon_min, lat_min, lon_max]
    # better to do rouding of bounding_box lat/lon
    bounding_box = [math.ceil(lat_max), math.floor(lon_min), 
                    math.floor(lat_min), math.ceil(lon_max)]
    
    file_name =  str(year) + '_' + str(month) + '_' + str(day) + '.grib'
    
    # create a directory to store retrieved data files along the route
    directory_path = 'era5_' + str(round(lat_max, 2)) + ',' +\
        str(round(lon_min, 2)) + ',' + str(round(lat_min, 2)) + ',' +\
            str(round(lon_max, 2))
    os.makedirs(directory_path, exist_ok=True)
    
    era5_file_location = os.path.join(directory_path, file_name)
    c.retrieve('reanalysis-era5-land', {'variable': ['10m_u_component_of_wind', 
                                                     '10m_v_component_of_wind', 
                                                     '2m_temperature'],
                                        'year': str(year),
                                        'month': str(month),
                                        'day': str(day),
                                        'time': ['00:00', '01:00', '02:00',
                                                 '03:00', '04:00', '05:00',
                                                 '06:00', '07:00', '08:00',
                                                 '09:00', '10:00', '11:00',
                                                 '12:00', '13:00', '14:00',
                                                 '15:00', '16:00', '17:00',
                                                 '18:00', '19:00', '20:00',
                                                 '21:00', '22:00', '23:00'],
                                        'area': bounding_box,
                                        'format': 'grib'}, era5_file_location)
    
    # add timeout options here
    
    return era5_file_location


#%% functions to convert grib latLonValues to df

def grib_vals_to_dict(data_messages):
    """
    Convert grib data messages for a single weather parameter into dictionary 
    of dataframes.
    
    Parameters
    ----------
    data_messages : gribmessage
        Data components in the grib file.

    Returns
    -------
    data_dict : dict
        Dictionary format made from grib data message.
        Keys are the lat/lons and values are data DFs.
    """
    df = pd.DataFrame()
    for msg in data_messages:
        #vals = wind_u[0]
        vals = msg.data()
        data = vals[0].reshape(np.size(vals[0]))
        lats = vals[1].reshape(np.size(vals[1]))
        lons = vals[2].reshape(np.size(vals[2]))
        
        temp_df = pd.DataFrame()
        temp_df['latlons'] = list(zip(lats, lons))
        temp_df['data'] = list(data)
        df = df.append(temp_df)
    
    latlons = list(zip(lats, lons))
    
    data_dict = {latlon: df[df.latlons == latlon] 
                 for latlon in latlons}
    
    return data_dict
    
    
#%%  function to extract data for locations along the route from grib datafile

def parse_era5_data(era5_file_location):
    """
    Read grib data file and return its weather parameters in a dictionary 
    format.
    
    Parameters
    ----------
    era5_file_location : str
        Location of the downloaded file.

    Returns
    -------
    wind_u_dict : dict
        Wind U component data dictionary.
    wind_v_dict : dict
        Wind V component data dictionary.
    temperature_dict : dict
        Temperature data dictionary..

    """
    era5_data = pygrib.open(era5_file_location)
    
    wind_u = []
    wind_v = []
    temperature = []
    
    for msg in era5_data:
        if msg['shortName'] == '10u':
            wind_u.append(msg)
        elif msg['shortName'] == '10v':
            wind_v.append(msg)
        elif msg['shortName'] == '2t':
            temperature.append(msg)
    
    start = str(pd.to_datetime(wind_u[1].validDate))
    timestamp = pd.date_range(start, periods=24, freq='H')
    
    wind_u_dict = grib_vals_to_dict(wind_u)
    wind_v_dict = grib_vals_to_dict(wind_v)
    temperature_dict = grib_vals_to_dict(temperature)
    
    # set timestamps as index for the dfs
    wind_u_dict = {key: val.set_index(timestamp) 
                   for key, val in wind_u_dict.items()}
    wind_v_dict = {key: val.set_index(timestamp) 
                   for key, val in wind_v_dict.items()}
    temperature_dict = {key: val.set_index(timestamp) 
                        for key, val in temperature_dict.items()}
    
    era5_data.rewind()
    
    return wind_u_dict, wind_v_dict, temperature_dict


#%% temperature unit conversion

def convert_kelvin_to_celsius_df(temperature_df):
    """
    Parameters
    ----------
    temperature_df : df
        DF with temperature values in kelvin.

    Returns
    -------
    temperature_df : df
        DF with temperature values in celsius.

    """
    converted_temperature = convert_temperature(temperature_df.data, 
                                                'k', 'c')
    # create a new celsius temperature df
    temperature_celsius = pd.DataFrame()
    temperature_celsius['temperature'] = converted_temperature
    temperature_celsius.index = temperature_df.index
    
    return temperature_celsius


def convert_kelvin_to_celsius_dict(temperature_dict):
    """
    Parameters
    ----------
    temperature_dict : dict
        Dict with temperature values in kelvin.

    Returns
    -------
    corrected_temperature_dict : dict
        Dict with temperature values in celsius.

    """
    corrected_temperature_dict = {key: convert_kelvin_to_celsius_df(val) 
                                  for key, val in temperature_dict.items()}
    
    return corrected_temperature_dict


#%% wind speed

def calculate_wind_speed_df(wind_u_df, wind_v_df):
    """
    Parameters
    ----------
    wind_u_df : df
        DESCRIPTION.
    wind_v_df : df
        DESCRIPTION.

    Returns
    -------
    wind_speed_df : df
        DESCRIPTION.

    """
    wind_speed = np.sqrt(wind_u_df.data ** 2 + wind_v_df.data ** 2)
    
    # create a new wind speed df
    wind_speed_df = pd.DataFrame()
    wind_speed_df['wind_speed'] = wind_speed
    wind_speed_df.index = wind_u_df.index
    
    return wind_speed_df
   
    
def calculate_wind_speed_dict(wind_u_dict, wind_v_dict):
    """
    Parameters
    ----------
    wind_u_dict : dict
        DESCRIPTION.
    wind_v_dict : dict
        DESCRIPTION.

    Returns
    -------
    wind_speed_dict : dict
        DESCRIPTION.

    """
    wind_speed_dict = {key: calculate_wind_speed_df(val, wind_v_dict[key])
                       for key, val in wind_u_dict.items()}
    
    return wind_speed_dict
    

#%% wind_direction    

def calculate_wind_direction_df(wind_u_df, wind_v_df):
    """
    Parameters
    ----------
    wind_u_df : df
        DESCRIPTION.
    wind_v_df : df
        DESCRIPTION.

    Returns
    -------
    wind_dir_df : df
        DESCRIPTION.

    """
    wind_dir = np.arctan2(wind_u_df.data, wind_v_df.data)
    wind_dir_degree = np.degrees(wind_dir)
    
    # keep values between 0 and 360 degrees
    wind_dir_degree = wind_dir_degree + 360 % 360
    
    # create a new wind_dir_df
    wind_dir_df = pd.DataFrame()
    wind_dir_df['wind_dir'] = wind_dir_degree
    wind_dir_df.index = wind_u_df.index
    
    return wind_dir_df


def calculate_wind_direction_dict(wind_u_dict, wind_v_dict):
    """
    Parameters
    ----------
    wind_u_dict : dict
        DESCRIPTION.
    wind_v_dict : dict
        DESCRIPTION.

    Returns
    -------
    wind_direction_dict : dict
        DESCRIPTION.

    """
    wind_direction_dict = {key: calculate_wind_direction_df(val, 
                                                            wind_v_dict[key])
                           for key, val in wind_u_dict.items()}
    
    return wind_direction_dict
    

#%% function to do linear interpolation on wind and temperature data

def interpolate_meteo_data_df(meteo_df, meteo_name, freq, samples_required):
    """
    Parameters
    ----------
    meteo_df : df
        DESCRIPTION.
    meteo_name : str
        DESCRIPTION.
    freq : str
        DESCRIPTION.
    samples_required : int
        DESCRIPTION.

    Returns
    -------
    df : df
        DESCRIPTION.

    """
    interp = interp1d(meteo_df.index.astype(np.int64), meteo_df[meteo_name])
    
    new_ts = pd.date_range(meteo_df.index[0], freq=freq, 
                           periods=samples_required)
    new_ts_unix = new_ts.astype(np.int64)
    new_vals = interp(new_ts_unix)
    
    # make a new df
    df = pd.DataFrame()
    df[meteo_name] = new_vals
    df.index = new_ts
    
    return df
    

def interpolate_meteo_data_dict(meteo_dict, meteo_name, freq='1t', 
                                samples_required=1380):
    """
    Parameters
    ----------
    meteo_dict : dict
        DESCRIPTION.
    meteo_name : dict
        DESCRIPTION.
    freq : str, default is '1t'
        DESCRIPTION.
    samples_required : int, default is 1380
        DESCRIPTION.

    Returns
    -------
    interp_dict : dict
        DESCRIPTION.

    """
    interp_dict = {key: interpolate_meteo_data_df(val, meteo_name, freq, 
                                                  samples_required) 
                   for key, val in meteo_dict.items()}
    
    return interp_dict
