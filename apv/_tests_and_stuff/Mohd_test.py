# #
import os
from pandas.io.parsers import read_csv
from apv.settings import apv_system_settings
from apv.settings.apv_system_settings import Default as SystSettings
from apv.utils.files_interface import save_fig, df_from_file_or_folder
import pandas as pd
import apv.settings.user_paths as user_paths
from pathlib import Path
from datetime import datetime as dt
import numpy as np
import apv.utils.time as t
from matplotlib import pyplot as plt
from apv.utils.files_interface import save_fig
import apv
from apv.classes.weather_data import WeatherData
SimSettings = apv.settings.sim_settings.Simulation()
weatherObj = WeatherData(SimSettings=SimSettings)

# #
df_tmy = weatherObj.typical_day_of_month()
# #
df_tmy.head(10)

df_tmy['GHI'].loc[1, 8]
# #
# NOT NEEDED JUST NOW TO TEST

ADS_data = r"C:\Users\moham\Documents\agri-PV\data_downloads\insolation-data_2005-01-01_to_2021-01-01_lat-50.86351_lon-6.52946_time_step-1hour.csv"

df: pd.DataFrame = pd.read_csv(ADS_data, skiprows=42, sep=';')
df[['obs_start', 'obs_end']] = \
    df.iloc[:, 0].str.split('/', 1, expand=True)
df.set_index(
    pd.to_datetime(df['obs_end'], utc=True),  # "right-labeled" as inBR
    inplace=True
)
# #
df
# #
# filter out 29th Feb
mask = (df.index.is_leap_year) & (df.index.dayofyear == 60)
df = df[~mask]
df['Month'] = df.index.month
df['Day'] = df.index.day
df['Hour'] = df.index.hour
df['Minute'] = df.index.minute

df
# #
# Create TMY from 2005-2021 data
df_tmy = pd.pivot_table(df,
                        index=['Month', 'Day', 'Hour'],
                        values=['GHI', 'DHI'], aggfunc=np.mean)
# #
print(df_tmy)
df_tmy['GHI'].loc[1, 1, 1]

# #
df_day_sums = pd.pivot_table(
    df,
    index=['Month', 'Day'],
    values=['GHI'],
    aggfunc='sum')

df_day_sums
# #
# per month: 'mean' of GHI-daily-sums
# needed to get the day with GHI closest to the result

df_all = pd.pivot_table(
    df_day_sums, index='Month',
    values=['GHI'], aggfunc=['min', 'mean', 'max'])

df_all
# #
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(df_all)
ax.set_xlabel('Month')
ax.set_ylabel('Daily integral of global horizontal irradiation in [Wh m$^{-2}$]')
ax.legend(['Minimum', 'Mean', 'Maximum'], loc='upper right')
apv.utils.files_interface.save_fig(fig, 'daily integral_min_mean_max')

# #
for month in range(1, 13):
    df_all.loc[month, 'day_min'] = np.argmin(df_day_sums.loc[month])+1
    df_all.loc[month, 'day_max'] = np.argmax(df_day_sums.loc[month])+1
    df_all.loc[month, 'day_nearest_to_mean'] = np.argmin(
        abs(df_day_sums.loc[month]-df_all.loc[month, 'mean']))+1

df_all
# #

# #
################################################
number_of_hours = 0
for month in range(1, 13):
    days = 15
    for day in days:
        for hour in range(0, 24, 2):
            sim_date_time = f'{month}-{day}_{hour}h'
            if df_tmy['GHI'].loc[month, day, hour] > 50:
                number_of_hours += 1
print(number_of_hours)
# #

number_of_hours = 0
for month in range(6, 12, 2):
    print(month)
    day = (int(df_all['day_nearest_to_mean'].loc[month]))
    for hour in range(0, 24, 2):
        sim_date_time = f'{month}-{day}_{hour}h'
        if df_tmy['GHI'].loc[month, day, hour] > 50:
            number_of_hours += 1
print(number_of_hours)
# #
weatherObj.typical_day_of_month()
# #
number_of_hours = 0
for month in range(6, 14, 2):
    print(month)
    for hour in range(0, 24, 1):
        if df_tmy['GHI'].loc[month, hour] > 50:
            number_of_hours += 1
print(number_of_hours)

# #
results_folder = os.path.join(
    user_paths.results_folder, f'{SimSettings.sim_name}',
    f'{SystSettings.module_form}')

# #
results_folder

# #
source_file = \
    'TMY_insolation-data_2005-01-01_to_2021-01-01_lat-50.86351_lon-6.52946_time_step-1hour.csv'
path = user_paths.radiance_input_files_folder / Path(
    'satellite_weatherData/' + source_file)
ads_TMY = df_from_file_or_folder(str(path), header=None, delimiter=' ')
ads_TMY.columns = names = ['ghi', 'dhi']

# #
ads_TMY.head(25)
# #
GHI = int(ads_TMY['ghi'].loc[10])

GHI

# #
path = r"C:\Users\moham\Documents\agri-PV\results\APV_Morschenich\std_res-1\10\data\radiation_10-15_17h00.csv"
path2 = r"C:\Users\moham\Documents\agri-PV\results\APV_Morschenich\std_res-1\10\data\radiation_10-15_18h00.csv"
df = pd.read_csv(path)
df2 = pd.read_csv(path2)
# #


# #
