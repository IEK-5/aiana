# #
import matplotlib.pyplot as plt
import pvlib
from urllib3 import add_stderr_logger
import apv
import pandas as pd
import numpy as np
from apv.settings import user_paths

from apv.utils import files_interface


# ADS
SimSettings = apv.settings.simulation.Simulation()
SimSettings.apv_location = pvlib.location.Location(
    51.2217, 6.7761, altitude=45, tz='Europe/Berlin')  # düsseldorf
SimSettings.time_step_in_minutes = 60
APV_SystSettings = apv.settings.apv_systems.Default()
brObj = apv.br_wrapper.BR_Wrapper(SimSettings, APV_SystSettings)
brObj.setup_br()

# #


def compare_vs_time(df, qty: str, ads_year_label: str):

    fig, ax = plt.subplots(1, 1, figsize=(5, 5)
                           )
    df[f'{qty} - ADS'].plot(ylabel=f'{qty}  [W m'+'$^{-2}$]', label='ADS',
                            linewidth=0.4)
    df[f'{qty} - EPW'].plot(alpha=0.6, label='EPW', linewidth=0.4)
    title = f'{qty} - ADS-{ads_year_label} vs EPW'
    plt.title(title)
    plt.legend()
    files_interface.save_fig(
        fig, str(user_paths.results_folder/f'epw_vs_ads/{title}'))


def helper(df_ads: pd.DataFrame, ads_year_label: str, year=2019):
    """df: df_ads"""
    (tmydata, metadata) = pvlib.iotools.epw.read_epw(
        r'C:\Users\l.raumann\Documents\agri-PV\bifacial_radiance_files\EPWs\DEU_Dusseldorf.104000_IWEC.epw',
        coerce_year=year)
    df = df_ads.copy()
    df.rename(columns={'dni_Wm-2': 'DNI - ADS',
                       'dhi_Wm-2': 'DHI - ADS',
                       'ghi_Wm-2': 'GHI - ADS'
                       }, inplace=True)

    df.loc[:, 'DNI - EPW'] = tmydata.loc[:, 'dni']
    df.loc[:, 'DHI - EPW'] = tmydata.loc[:, 'dhi']
    df.loc[:, 'GHI - EPW'] = tmydata.loc[:, 'ghi']

    compare_vs_time(df, 'DNI', ads_year_label)
    compare_vs_time(df, 'GHI', ads_year_label)
    compare_vs_time(df, 'DHI', ads_year_label)


df_ads = brObj.weatherData.df_irradiance
for aggfunc in ['min', 'max', 'mean']:
    helper(brObj.weatherData.df_irradiance_to_TMY(df_ads, aggfunc=aggfunc),
           ads_year_label=f'{aggfunc} 2005-2020')

# #
# single years
for year in range(2005, 2021):
    df = df_ads[df_ads.index.year == year]
    helper(df, ads_year_label=str(year), year=year)
    # df.index = df_ads.index.shift(-1, freq='H'
