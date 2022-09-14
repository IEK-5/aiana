# #
import matplotlib.pyplot as plt
import pvlib
from urllib3 import add_stderr_logger
import apv
import pandas as pd
import numpy as np
from apv.settings import user_paths

from apv.utils import files_interface

from apv.classes.util_classes.settings_handler import Settings
from apv.classes.br_wrapper import BR_Wrapper

# ADS

settings = Settings()
settings.sim.apv_location = pvlib.location.Location(
    51.2217, 6.7761, altitude=45, tz='Europe/Berlin')  # düsseldorf
settings.sim.time_step_in_minutes = 60
brObj = BR_Wrapper(settings)


# #

def compare_vs_time(df, qty: str, ads_year_label: str):

    fig, ax = plt.subplots(1, 1, figsize=(5, 5)
                           )
    df[f'{qty} - ADS'].plot(ylabel=f'{qty}  [W m'+'$^{-2}$]', label='ADS',
                            linewidth=0.3)
    title = f'{qty} - ADS-{ads_year_label} vs EPW'  # ! epw is not clear sky !
    if qty == 'GHI_clearSky':
        qty = 'GHI'
    df[f'{qty} - EPW'].plot(alpha=0.6, label='EPW', linewidth=0.2)
    plt.title(title)
    plt.legend()
    files_interface.save_fig(
        fig, str(settings._paths.results_folder/f'epw_vs_ads/{title}'),
        dpi=400)


def helper(df_ads: pd.DataFrame, ads_year_label: str, year=2019):
    """df: df_ads"""
    (tmydata, metadata) = pvlib.iotools.epw.read_epw(
        settings._paths.bifacial_radiance_files/r'EPWs/DEU_Dusseldorf.104000_IWEC.epw',
        coerce_year=year)
    df = df_ads.copy()
    df.rename(columns={'dni_Wm-2': 'DNI - ADS',
                       'dhi_Wm-2': 'DHI - ADS',
                       'ghi_Wm-2': 'GHI - ADS',
                       'ghi_clearSky_Wm-2': 'GHI_clearSky - ADS'
                       }, inplace=True)

    df.loc[:, 'DNI - EPW'] = tmydata.loc[:, 'dni']
    df.loc[:, 'DHI - EPW'] = tmydata.loc[:, 'dhi']
    df.loc[:, 'GHI - EPW'] = tmydata.loc[:, 'ghi']

    #compare_vs_time(df, 'DNI', ads_year_label)
    #compare_vs_time(df, 'GHI', ads_year_label)
    compare_vs_time(df, 'DHI', ads_year_label)
    #compare_vs_time(df, 'GHI_clearSky', ads_year_label)


for aggfunc in ['min', 'max', 'mean', 'median']:
    brObj.settings.sim.TMY_irradiance_aggfunc = aggfunc
    helper(brObj.weatherData.df_irradiance_to_TMY(),
           ads_year_label=f'{aggfunc} 2005-2020')


# #

# #
# single years
for year in range(2005, 2021):
    df = df_ads[df_ads.index.year == year]
    helper(df, ads_year_label=str(year), year=year)
    # df.index = df_ads.index.shift(-1, freq='H'


# #


# #
# non- tmy (complete)
df_all = brObj.weatherData.load_and_process_insolation_data()
df_all['ghi_clearSky_Wm-2'].std()
# #
df_all['ghi_clearSky_Wm-2'].mean()
# #
maxlist = []
for year in range(2005, 2022):
    df = df_all[df_all.index.year == year]
    # df.index=range(len(df.index))
    df['ghi_clearSky_Wm-2'].plot(linewidth=0.1, label=year)
    maxlist += [df['ghi_clearSky_Wm-2'].max()]
plt.legend()
# #
np.std(maxlist)
np.mean(maxlist)

# #
df_tdm = brObj.weatherData.df_irradiance_typ_day_per_month
cumulative_GHIs = {}
df = df_all.copy()
for month in range(1, 13):
    df[df.index.month == month]['ghi_Wm-2'] = np.where(df[df.index.month == month]['ghi_Wm-2'] < min(
        df_tdm.loc[(month), 'ghi_Whm-2'].sum() * 0.02, 50), 0, df[df.index.month == month]['ghi_Wm-2'])
df

# #
df_ghi_filters = pd.DataFrame()
for month in range(1, 7):
    for threshold in range(4, 61):
        df_month = df_all[df_all.index.month == month]
        df_filtered = df_month[df_month['ghi_Wm-2'] >= threshold]
        df_ghi_filters.loc[threshold, month] = \
            100-100*df_filtered['ghi_Wm-2'].sum() / df_month['ghi_Wm-2'].sum()
    df_ghi_filters.plot()
plt.yscale('log')
plt.xlabel('ignored GHI threshold [W/m²]')
plt.ylabel('missing data [%]')
plt.grid()
