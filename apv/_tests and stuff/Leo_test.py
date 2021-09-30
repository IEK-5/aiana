# #
from apv.classes.sim_datetime import SimDT
import pvlib
from apv.classes.weather_data import WeatherData
from apv.utils import files_interface
import apv.utils.files_interface as fi
from apv.classes.geometries_handler import GeometriesHandler
import re
import apv.settings.user_pathes as user_pathes
from typing import Literal
from datetime import datetime as dt
import hjson
from types import SimpleNamespace
from pathlib import Path
import apv
import subprocess
import numpy as np
import pandas as pd
import json
import os
import pytictoc
from apv.utils import files_interface as fi
from apv import settings
from apv import br_wrapper as br
import importlib as imp
import sys
import time
import random
from apv.settings import apv_systems
import pandas
import pytz
from pandas.tseries.offsets import Minute
import honeybee_radiance_command as hrc


# #
# import this


SimSettings = apv.settings.simulation.Simulation()
simdt = SimDT(SimSettings)
weatherObj = WeatherData()

download_file_path = weatherObj.download_insolation_data(
    SimSettings.apv_location,
    '2005-01-01/2021-01-01', '1hour')
source_file_path = download_file_path

file_name = 'TMY_'+str(source_file_path).split('\\')[-1]
tmy_folder_path = user_pathes.bifacial_radiance_files_folder / Path(
    'satellite_weatherData')

tmy_file_path = tmy_folder_path/file_name

"""
if tmy_file_path.exists():
    return apv.utils.files_interface.df_from_file_or_folder(
        tmy_file_path, delimiter=' ', names=['ghi', 'dhi']
    )
"""
# else:
apv.utils.files_interface.make_dirs_if_not_there(tmy_folder_path)

df: pd.DataFrame = pd.read_csv(source_file_path, skiprows=42, sep=';')
df[['obs_start', 'obs_end']] = \
    df.iloc[:, 0].str.split('/', 1, expand=True)
df.set_index(
    pd.to_datetime(df['obs_end'], utc=True),  # "right-labeled" as inBR
    inplace=True
)

# filter out 29th Feb
mask = (df.index.is_leap_year) & (df.index.dayofyear == 60)
df = df[~mask]

# split time stamp for pivot

df['Month'] = df.index.month
df['Day'] = df.index.day
df['Hour'] = df.index.hour
df['Minute'] = df.index.minute
df
# #
df_mean_hours_per_month = pd.pivot_table(
    df,
    index=['Month', 'Hour'],
    values=['GHI', 'DHI'],
    aggfunc='mean')
df_mean_hours_per_month.query('GHI > 0')

df_mean_hours_per_month.plot()
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

for month in range(1, 13):
    df_all.loc[month, 'day_min'] = np.argmin(df_day_sums.loc[month])+1
    df_all.loc[month, 'day_max'] = np.argmax(df_day_sums.loc[month])+1
    df_all.loc[month, 'day_nearest_to_mean'] = np.argmin(
        abs(df_day_sums.loc[month]-df_all.loc[month, 'mean']))+1

df_all

# #
df_all.plot()


# #

df_tmy[df_tmy['DHI'] > 40]


# #
str(simdt.sim_dt_utc)

# #

"""
-
- sun position time
"""

sun_loc_time_str = str(simdt.sim_dt_utc_pd-pd.Timedelta('30min'))
sun_loc_time_str
# #

# #
now_utc = dt.utcnow()
print(now_utc)

tz = pytz.timezone('Europe/Berlin')
now_kl = now_utc.replace(tzinfo=pytz.utc).astimezone(tz)


print(type(now_kl))
now_kl
# #
times = now_kl
solar_position = SimSettings.apv_location.get_solarposition(
    times=times)
type(solar_position)
float(solar_position.zenith)
solar_position.zenith[0]
# #


# #
fi.df_from_file_or_folder(
    user_pathes.bifacial_radiance_files_folder/Path(
        'satellite_weatherData/TMY_nearJuelichGermany.csv'
        # TODO make it automatic with mohds method
    ), names=['ghi', 'dhi'], delimiter=' '
)
# #
rad_mat_file: Path = user_pathes.bifacial_radiance_files_folder / Path(
    'materials/ground2.rad')

mat_name = 'grass'
# check for existence:
with open(rad_mat_file, 'r') as f:
    lines: list = f.readlines()
    f.close()

with open(rad_mat_file, 'w') as f:
    print_string = 'new'
    for i, line in enumerate(lines):
        if mat_name in line:
            f.writelines(lines[:i-1] + lines[i+4:])
            print_string = 'existing'
            break
    f.close()
print(print_string)


# data.index('void plastic black\n')
# #
[mat_name in line for line in data]

# #
test = ['0', '1', '2', '3', '4']

del_line_start = 1
number_of_follow_lines_to_delete = 45
del_line_to = del_line_start+number_of_follow_lines_to_delete

data[:del_line_start] + data[del_line_to+1:]


# #
if any([mat_name in line for line in data]):
    print(f'material {mat_name} already exists')
    # TODO: better: delete 4 lines to "overwrite"
# #


class test(apv.settings.apv_systems.Default):

    sceneDict = {'tilt': 40,
                 'pitch': 10,
                 'hub_height': 4.5,
                 'azimuth': 180,
                 'nMods': 10,
                 'nRows': 3,
                 }


test.sceneDict
test.moduleDict
# #

sceneDict = {
    'tilt': 20,
    'pitch': 10,
    'hub_height': 4.5,
    'azimuth': 180,
    'nMods': 10,
    'nRows': 3,
}

moduleDict = {
    'x': 0.998,
    'y': 1.980,
    'xgap': 0.005,
    'ygap': 0.05,
    'zgap': 0,
    'numpanels': 2
}

# #
test.sceneDict['azimuth']

# #

sceneDict['tilt'] = 10


# #
def get_hour_of_year(date_time_str: str) -> int:
    """converts str to hours_of_year

    Args:
        date_time_str (str): format: 'month-day_hour'+'h',
        e.g.'06-15_10h'

    Returns:
        int: hours_of_year
    """
    date_time_obj = datetime.strptime(date_time_str, '%m-%d_%Hh')

    date_time_str_ref = '01-01_00h'
    date_time_obj_ref = datetime.strptime(date_time_str_ref, '%m-%d_%Hh')

    delta = date_time_obj - date_time_obj_ref
    return delta.days * 24 + date_time_obj.hour


get_hour_of_year('06-15_9h')
# #

get_hour_of_year('06-17_12h')
# #
imp.reload(apv)
# #


class Test():
    x = 1

    def __init__(self):
        self.y = 3

    def method(self):
        print(self.x)
        print(self.y)

    @ classmethod
    def class_method(cls):
        print(cls.x)

    @ staticmethod
    def static_method(string='hi'):
        print(string)


t = Test()
t.x = 2

print('method:')
t.method()
print('class method:')
t.class_method()
print('static method:')
t.static_method()


print('x not changed')
t = Test()
print('method:')
t.method()
print('class method:')
t.class_method()
print('static method:')
t.static_method('hi2')
# #


class Test():
    x = 1

    def method(self):
        print(self.x)

    @ classmethod
    def class_method(cls):
        print(cls.x)


t = Test()
t.x = 2
print('method:')
t.method()
print('class method:')
t.class_method()

# #


class Test():
    x = 1

    def __init__(self):
        self.y = 1

    def method(self):
        print(self.x)
        # print(self.y)


t = Test()
t2 = Test()
t2.x = 2
t.method()
Test.x = 3
t.method()
t2.method()


# #

def clear(): return os.system('clear')


for i in range(2):
    for i in range(1, 4):
        clear()
        print('Loading' + "."*i)
        time.sleep(0.5)
# #


class Test():
    x = 1

    def __init__(self):
        self.y = 1

    def method(self):
        print(self.y)
        # print(self.y)


t = Test()
t2 = Test()
t2.y = 2
t.method()
Test.y = 3
t.method()
t2.method()
t3 = Test()
t3.method()
# t2.method()
# #
x = br.setup_br(sky_gen_type='gendaylit', cellLevelModule=False, EPW=True)
# #
print(x)

# !!
print(type(x[2]))
# !!
testfolder = up.root_folder
View_scene = os.path.join(testfolder, 'views', 'overall.vp')
with open(View_scene, 'w') as f:
    f.write('rvu -vtv -vp '              # vp = view port
            + '-15 '                     # X (depth)
            + '-1.8 '                    # Y (left / right)
            + '6 '                       # Z (height)
            + '-vd 1.581 0 -0.519234 '   # vd = view direction
            + '-vu 0 0 1 '               # vu = view "Up" ???
            + '-vh 110 -vv 45 '          # vh/vv = horizonor
            + '-vs 0 -vl 0')             # vs/vl:
br.view_scene(view_fp=View_scene, oct_file_name='APV_floating')
# !!

br.ground_simulation(radObj=x[0], scene=x[2], oct_file_name=x[1])

# !!
print(type(s.start_time))


# #

a = 'ab'
s = '2+len(a)'
eval(s)

# #
text = """{
    test: {
        foo: 2
        bar: 1
    }
}"""

data = hjson.loads(text)


# #
str(apv.settings.user_pathes.data_download_folder)

# #

# Parse JSON into an object with attributes corresponding to dict keys.
x = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

# #
d2 = dotdict(d)
d2.test.foo
# 'it works'
# #
mydict.nested = dotdict(nested_dict)
mydict.nested.val
# 'nested works too'

# #
root_folder = (Path().home().resolve() / 'Documents' /
               'Python_Scripts' / 'parameter_study')
p = root_folder / r'Trading\test'
str(p)
