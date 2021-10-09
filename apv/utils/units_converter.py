# #
"""Converts final results units
       """
from numpy.core.fromnumeric import std
from apv.settings import simulation
from apv.classes.sim_datetime import SimDT
from apv.utils import files_interface
from apv.settings.simulation import Simulation
from pathlib import Path
from apv.settings import user_pathes
import numpy as np
from typing import Literal
from apv.classes.weather_data import WeatherData


def irradiance_to_PAR(df=None):
    """Converts irradiance from [W/m2] to
     Photosynthetic Active Radiation PAR [μmol quanta/ m2.s] [1]

     [1] Čatský, J. (1998): Langhans, R.W., Tibbitts, T.W. (ed.):
     Plant Growth Chamber Handbook. In Photosynt. 35 (2), p. 232.
     DOI: 10.1023/A:1006995714717.

     Args:
         groundscan (DataFrame): [description]
     """

    df['PARGround'] = df['Wm2'] * 4.6

    return df

# #


def irradiance_to_shadowdepth(df, SimSettings, strt=None, enddt=None,
                              cumulative=False):
    """Shadow Depth is loss of incident solar energy in comparison
    with a non intersected irradiation; if 90% of irradiation available after
    being intersected by objects then the shadow depth is 10% [1][2].

    [1] Miskin, Caleb K.; Li, Yiru; Perna, Allison; Ellis, Ryan G.; Grubbs,
    Elizabeth K.; Bermel, Peter; Agrawal, Rakesh (2019): Sustainable
    co-production of food and solar power to relax land-use constraints. In
    Nat Sustain 2 (10), pp. 972–980. DOI: 10.1038/s41893-019-0388-x.

    [2] Perna, Allison; Grubbs, Elizabeth K.; Agrawal, Rakesh; Bermel, Peter
    (2019): Design Considerations for Agrophotovoltaic Systems: Maintaining PV
    Area with Increased Crop Yield. DOI: 10.1109/PVSC40753.2019.8981324

    Args:
        df (DataFrame): The DataFrame with W.m^-2 values
        SimSettings : self.SimSettings should be given.
        strt (['M-D_H:m], optional): only in case specific period need to be
        converted in cumulative form. Defaults to None and read from
        SimSettings.
        enddt ([M-D_H:m], optional): only in case specific period need to be
        converted in cumulative form. Defaults to None and read from
        SimSettings.
        cumulative (bool, optional): used only if cumulative data were used.
        Gencumsky turns this automaticaly to True. Defaults to False.

    Returns:
        [type]: [description]
    """
    simDT = SimDT(SimSettings)
    weatherObj = WeatherData(SimSettings=SimSettings)
    download_file_path = weatherObj.download_insolation_data(
        SimSettings.apv_location,
        '2005-01-01/2021-01-01', '1hour')
    # make/read own TMY data
    ADS_irradiance = weatherObj.satellite_insolation_data_to_TMY(
        download_file_path)

    if SimSettings.sky_gen_mode == 'gendaylit':
        sim_time = simDT.convert_settings_localtime_to_UTC(
            SimSettings.sim_date_time, SimSettings.apv_location.tz)
        timeindex = simDT.get_hour_of_tmy(sim_time)
        GHI = int(ADS_irradiance['ghi'].loc[timeindex])
        df['ShadowDepth'] = 100 - ((df['Wm2']/GHI)*100)

    elif SimSettings.sky_gen_mode == 'gencumsky' or cumulative:
        cumulative_GHI = 0
        strt = simDT.convert_settings_localtime_to_UTC(
            strt, SimSettings.apv_location.tz) or \
            simDT.convert_settings_localtime_to_UTC(
            SimSettings.startdt, SimSettings.apv_location.tz)

        endt = simDT.convert_settings_localtime_to_UTC(
            enddt, SimSettings.apv_location.tz) or\
            simDT.convert_settings_localtime_to_UTC(
            SimSettings.enddt, SimSettings.apv_location.tz)
        stdt = simDT.get_hour_of_tmy(strt)
        enddt = simDT.get_hour_of_tmy(endt)

        for timeindex in np.arange(stdt, enddt+1):
            GHI = int(ADS_irradiance['ghi'].loc[timeindex])
            cumulative_GHI += GHI
        df['ShadowDepth'] = 100 - ((df['Wm2']/cumulative_GHI)*100)
    return df


def convert_units(SimSettings, df=None, cumulative=False):
    if 'PARGround' not in df.columns:
        df = irradiance_to_PAR(df=df)

    df = irradiance_to_shadowdepth(df=df, SimSettings=SimSettings,
                                   cumulative=cumulative)
    if cumulative or SimSettings.cm_unit == 'Irradiation':
        df.rename(columns={"Wm2": "Whm2"}, inplace=True)
    return df


def get_units_parameters(cm_unit=None):
    if cm_unit == 'PAR':
        unit_parameters = {'z': 'PARGround', 'colormap': 'YlOrBr',
                           'z_label': 'PAR [μmol quanta.m$^{-2}$.s$^{-1}$]'}

    elif cm_unit == 'Irradiation':
        unit_parameters = {
            'z': 'Whm2',  'colormap': 'inferno',
            'z_label': 'Cumulative Irradiance on Ground [Wh m$^{-2}$]'}

    elif cm_unit == 'Shadow-Depth':
        unit_parameters = {'z': 'ShadowDepth',  'colormap': 'viridis_r',
                           'z_label': 'Shadow-Depth [%]'}
    else:
        unit_parameters = {'z': 'Wm2', 'colormap': 'inferno',
                           'z_label': 'Irradiance on Ground [W m$^{-2}$]'}

    return unit_parameters
