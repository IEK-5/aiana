# #
"""Converts final results units
       """
from numpy.core.fromnumeric import std
from apv.settings import simulation
from apv.utils import time
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

    df['PARGround'] = df['Wm2Ground'] * 4.6

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
    path = user_pathes.bifacial_radiance_files_folder / Path(
        'EPWs' + '/epw_temp.csv')
    epw = files_interface.df_from_file_or_folder(path, header=None)

    if SimSettings.sky_gen_mode == 'gendaylit':
        timeindex = time.get_hour_of_year(SimSettings.sim_date_time)
        GHI = int(epw.loc[timeindex][0].split()[0])
        df['ShadowDepth'] = 100 - ((df['Wm2Ground']/GHI)*100)

    else:
        cumulative_GHI = 0
        stdt = time.get_hour_of_year(SimSettings.startdt)
        enddt = time.get_hour_of_year(SimSettings.enddt)
        for timeindex in np.arange(stdt, enddt):
            GHI = int(epw.loc[timeindex][0].split()[0])
            cumulative_GHI += GHI
        df['ShadowDepth'] = 100 - ((df['Wm2Ground']/cumulative_GHI)*100)
    return df
