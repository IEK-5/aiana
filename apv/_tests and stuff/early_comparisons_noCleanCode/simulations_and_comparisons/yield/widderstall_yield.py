# #
import pvlib
import apv
# import apv.resources
import pandas as pd
import numpy as np

import importlib as imp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import apv.settings.user_paths as user_paths


# #

input_folder = Path.cwd().parent.parent.parent.parent/'resources/pv_modules'
input_folder
# #
pv_module: pd.Series = apv.utils.files_interface.df_from_file_or_folder(
    input_folder+'\\Sanyo240_moduleSpecs_guestimate.txt',
    delimiter='\t').T[0]
pv_module  # a series

# #

df = apv.utils.files_interface.df_from_file_or_folder(
    'raw-data/sanyo', skiprows=9, append_all_in_folder=True, delimiter='\t')

df
# #
# set unreasonable data to NaN
df['Voc'] = np.where(df['POA'] < 0, np.nan, df['Voc'])
df['Voc'] = np.where(df['Voc'] < 25, np.nan, df['Voc'])


def sim_poa(df):
    df = apv.utils.time.column_to_utc_index(df, 'Datum', 'Etc/GMT-1')

    # POA sim
    site = pvlib.location.Location(
        48.533, 9.717, altitude=750, tz='Europe/Berlin')

    # Get solar azimuth and zenith to pass to the transposition function
    solar_position = site.get_solarposition(times=df.index)

    DNI = (df['GHI'] - df['DHI']) / np.cos(
        solar_position['apparent_zenith']*np.pi/180)

    df_POA_irradiance = pvlib.irradiance.get_total_irradiance(
        surface_tilt=40,    # from widderstall description file
        surface_azimuth=180,  # "
        dni=DNI,
        ghi=df['GHI'],
        dhi=df['DHI'],
        solar_zenith=solar_position['apparent_zenith'],
        solar_azimuth=solar_position['azimuth'],
        # model='klucher'
    )

    df['POA_sim'] = df_POA_irradiance['poa_global']
    apv.utils.files_interface.df_export(
        df, 'poa_widderstall', rel_path='processed-data')

    return df


df = sim_poa(df)

df['Tcell'] = pvlib.temperature.sapm_cell(
    df['POA_sim'], df['TAA'], df['VW'],
    pv_module['A'], pv_module['B'], pv_module['DTC']
)

dc = pvlib.pvsystem.sapm(df['POA'], df['Tcell'], pv_module)

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

    apv.tools.files_interface.save_fig(
        apv.tools.plots.comparing_plot_sns(df, x, y, units[i]),
        file_name='Widderstall_' + x_list[i] + '_POAsim', rel_path='results',
        dpi=500)


# #
df['experimental $V_{oc}$'].min()
# #
