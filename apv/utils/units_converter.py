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


def irradiance_to_shadowdepth(df, SimSettings):
    """ Shadow Depth is loss of incident solar energy in comparison
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
           df ([type], optional): [description]. Defaults to None.
       """
    simDT = SimDT(SimSettings)
    path = user_pathes.bifacial_radiance_files_folder / Path(
        'EPWs' + '/epw_temp.csv')
    epw = files_interface.df_from_file_or_folder(str(path), header=None)

    if SimSettings.sky_gen_mode == 'gendaylit':
        sim_time = simDT.convert_settings_localtime_to_UTC(
            SimSettings.sim_date_time, SimSettings.apv_location.tz)
        timeindex = simDT.get_hour_of_tmy(sim_time)
        GHI = int(epw.loc[timeindex][0].split()[0])
        df['ShadowDepth'] = 100 - ((df['Wm2']/GHI)*100)

    else:
        cumulative_GHI = 0
        strt = simDT.convert_settings_localtime_to_UTC(
            SimSettings.startdt, SimSettings.apv_location.tz)
        endt = simDT.convert_settings_localtime_to_UTC(
            SimSettings.enddt, SimSettings.apv_location.tz)
        stdt = simDT.get_hour_of_tmy(strt)
        enddt = simDT.get_hour_of_tmy(endt)
        for timeindex in np.arange(stdt, enddt+1):
            GHI = int(epw.loc[timeindex][0].split()[0])
            cumulative_GHI += GHI
        df['ShadowDepth'] = 100 - ((df['Wm2']/cumulative_GHI)*100)
    return df
