import pandas as pd
# import shutil
import pvlib

# ######### ADS #################
import cdsapi

'2015-01-01/2015-01-02'

def download_ads_data(
    file_name: str,
    location: pvlib.location,
    date_range=str,
    time_step='15minute'
):
    """
    method to download via API request satelite based insolation data
    taking into account the observed weather

    Args:
        file_name (str): file name, where the data is stored to
        location (pvlib.location): pvlib location object to pass coordinates
        date (str): start and end date in the format '2015-01-01/2015-01-02'
        time_step (str, optional): time step, e.g. '15minute', or '1hour'
        
    for access, one needs to register and store a key file on the pc
    more info:
    https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-solar-radiation-timeseries?tab=form
    """

    c = cdsapi.Client()
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
        file_name + '.csv')

    # move file
    # source = os.path.join(os.path.dirname(__file__), file_name+'.csv')
    # destination = os.path.join(rel_destination_sub_folder, file_name+'.csv')
    # shutil.move(source, destination)


# ########### NSRDB ################


def retrieve_nsrdb_data(
        lat, lon, year=2019, interval=15,
        attributes='ghi,dhi,dni,wind_speed,air_temperature,surface_albedo'
        ) -> pd.DataFrame:
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


#df = retrieve_nsrdb_data(
#    50.941, 6.367, year=2021, interval=15,
#    attributes='ghi,dhi,dni,wind_speed,air_temperature,surface_albedo')
#df
