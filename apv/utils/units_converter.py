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


def add_PAR(df=None):
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


def add_shadowdepth(df, SimSettings: Simulation, cumulative=False):
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
        start_dt_loc (['M-D_H:m], optional): only in case specific period need
        to be converted to cumulative form. Defaults to None and read from
        SimSettings.
        end_dt_loc ([M-D_H:m], optional): only in case specific period need to
        be converted to cumulative form. Defaults to None and read from
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
    # TODO at the moment TMY data is hourly and indexed by hour of year
    # problem for higher time resolution: not compatible with
    # gencumsky of br, and date-time index needs a year, should we take
    # a random non-leap-year for this?
    ADS_irradiance = weatherObj.satellite_insolation_data_to_TMY(
        download_file_path)

    if SimSettings.sky_gen_mode == 'gendaylit' and not cumulative:
        sim_time = simDT.convert_settings_localtime_to_UTC(
            SimSettings.sim_date_time, SimSettings.apv_location.tz)
        timeindex = simDT.get_hour_of_tmy(sim_time)
        GHI = int(ADS_irradiance['ghi'].loc[timeindex])
        df['ShadowDepth'] = 100 - ((df['Wm2']/GHI)*100)

    elif SimSettings.sky_gen_mode == 'gencumsky' or cumulative:
        cumulative_GHI = ADS_irradiance['ghi'].loc[
            simDT.start_hour_of_tmy:simDT.end_hour_of_tmy+1].sum()

        df['ShadowDepth_cum'] = 100 - ((df['Whm2']/cumulative_GHI)*100)
    return df


def get_label_and_cm_input(cm_unit, cumulative):
    """for the heatmap"""

    if not cumulative:

        if cm_unit == 'radiation':
            unit_parameters = {'z': 'Wm2', 'colormap': 'inferno',
                               'z_label': 'Irradiance on Ground [W m$^{-2}$]'}

        elif cm_unit == 'shadow_depth':
            unit_parameters = {'z': 'ShadowDepth',  'colormap': 'viridis_r',
                               'z_label': 'shadow_depth [%]'}

        elif cm_unit == 'PAR':
            unit_parameters = {
                'z': 'PARGround', 'colormap': 'YlOrBr',
                'z_label': 'PAR [μmol quanta.m$^{-2}$.s$^{-1}$]'}
        else:
            print('cm_unit has to be radiation, shadow_depth or PAR')

    elif cumulative:

        if cm_unit == 'radiation':
            unit_parameters = {
                'z': 'Whm2',  'colormap': 'inferno',
                'z_label': 'Cumulative Irradiation on Ground [Wh m$^{-2}$]'}

        elif cm_unit == 'shadow_depth':
            unit_parameters = {'z': 'ShadowDepth_cum',  'colormap': 'viridis_r',
                               'z_label': 'Cumulative Shadow Depth [%]'}

        elif cm_unit == 'PAR':  # TODO unit changes also to *h ?
            unit_parameters = {
                'z': 'PARGround_cum', 'colormap': 'YlOrBr',
                'z_label': 'Cumulative PAR [μmol quanta.m$^{-2}\cdot s^{-1}$]'}
        else:
            print('cm_unit has to be radiation, shadow_depth or PAR')
    return unit_parameters
