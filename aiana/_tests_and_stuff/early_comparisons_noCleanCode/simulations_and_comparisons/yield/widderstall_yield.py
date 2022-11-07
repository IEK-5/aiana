# #
import pvlib
import aiana
# import apv.resources
import pandas as pd
import numpy as np

import importlib as imp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import aiana.settings.user_paths as user_paths
from aiana.utils.files_interface import df_export


# #

input_folder = Path.cwd().parent.parent.parent.parent/'resources/pv_modules'
input_folder
# #
pv_module: pd.Series = aiana.utils.files_interface.df_from_file_or_folder(
    input_folder/'Sanyo240_moduleSpecs_guestimate.txt',
    delimiter='\t').T[0]
pv_module  # a series

# #

df = aiana.utils.files_interface.df_from_file_or_folder(
    r'C:\Users\l.raumann\Documents\agri-PV\raw-data\sanyo',
    skiprows=9, append_all_in_folder=True, delimiter='\t'
)

# #
df = aiana.utils.time.column_to_utc_index(df, 'Datum', 'Etc/GMT-1')

# set unreasonable data to NaN and drop them
df['Voc'] = np.where(df['POA'] < 0, np.nan, df['Voc'])
df['Voc'] = np.where(df['Voc'] < 25, np.nan, df['Voc'])
df.dropna(inplace=True)

site = pvlib.location.Location(
    48.533, 9.717, altitude=750, tz='Europe/Berlin')

# Get solar azimuth and zenith to pass to the transposition function
solar_position = site.get_solarposition(times=df.index)
df['GHI'] = np.where(df['GHI'] < df['DHI'], df['DHI'], df['GHI'])
dni: pd.Series = (df['GHI'] - df['DHI']) / np.cos(
    solar_position['apparent_zenith']*np.pi/180)
dni2 = pvlib.irradiance.dni(
    df['GHI'], df['DHI'], solar_position['apparent_zenith'])

test = dni-dni2

test
# #


def sim_poa(df, model='isotropic'):
    df = aiana.utils.time.column_to_utc_index(df, 'Datum', 'Etc/GMT-1')

    # set GHI >= DHI (data contains GHI < DHI, which makes no sense):
    df['GHI'] = np.where(df['GHI'] < df['DHI'], df['DHI'], df['GHI'])
    # POA sim
    site = pvlib.location.Location(
        48.533, 9.717, altitude=750, tz='Europe/Berlin')

    # Get solar azimuth and zenith to pass to the transposition function
    solar_position = site.get_solarposition(times=df.index)

    # dni: pd.Series = (df['GHI'] - df['DHI']) / np.cos(
    #    solar_position['apparent_zenith']*np.pi/180)
    # (differences to following < e-15)
    dni = pvlib.irradiance.dni(
        df['GHI'], df['DHI'], solar_position['apparent_zenith'])

    df_POA_irradiance = pvlib.irradiance.get_total_irradiance(
        surface_tilt=40,    # from widderstall description file
        surface_azimuth=180,  # "
        # accounting for armospheric diffraction:
        solar_zenith=solar_position['apparent_zenith'],
        solar_azimuth=solar_position['azimuth'],
        dni=dni,
        ghi=df['GHI'],
        dhi=df['DHI'],
        model=model
    )

    df['POA_sim'] = df_POA_irradiance['poa_global']
    return df


for model in [
    # 'isotropic',
    'perez'
]:
    df = aiana.utils.files_interface.df_from_file_or_folder(
        r'C:\Users\l.raumann\Documents\agri-PV\raw-data\sanyo',
        skiprows=9, append_all_in_folder=True, delimiter='\t'
    )

    df = sim_poa(df, model=model)

    aiana.utils.files_interface.df_export(
        df, f'poa_widderstall_{model}', rel_path='processed-data')


# #

df['Tcell'] = pvlib.temperature.sapm_cell(
    df['POA_sim'], df['TAA'], df['VW'],
    pv_module['A'], pv_module['B'], pv_module['DTC']
)

dc = pvlib.pvsystem.sapm(df['POA'], df['Tcell'], pv_module)


# set unreasonable data to NaN and drop them
df['Voc'] = np.where(df['POA'] < 0, np.nan, df['Voc'])
df['Voc'] = np.where(df['Voc'] < 25, np.nan, df['Voc'])
df.dropna(inplace=True)

# plotting

# labels for x and y to be used in the comparison plot
x_list = ['Isc', 'Voc', 'Pmpp']
x_list_renamed = [
    'experimental $I_{sc}$',
    'experimental $V_{oc}$',
    'experimental $P_{mpp}$']

y_list = ['i_sc', 'v_oc', 'p_mp']
y_list_renamed = [
    'simulated $I_{sc}$',
    'simulated $V_{oc}$',
    'simulated $P_{mpp}$']

units = ['A', 'V', 'W']

for i in range(len(x_list)):
    x = x_list_renamed[i]
    y = y_list_renamed[i]
    df.rename(columns={x_list[i]: x}, inplace=True)
    df[x] = df[x].astype(float)
    df[y] = dc[y_list[i]]

    aiana.tools.files_interface.save_fig(
        aiana.tools.plots.comparing_plot_sns(df, x, y, units[i]),
        file_name='Widderstall_' + x_list[i] + '_POAsim', rel_path='results',
        dpi=500)


# #
df['experimental $V_{oc}$'].min()
# #
