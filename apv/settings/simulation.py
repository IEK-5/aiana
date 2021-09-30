# #
"""Important infos
sim_date_time = 12h will at the moment result in irradiation data
11-12h and sol position 11:30 !
(bifacial radiance uses righ-labled timestamps and does it this way)
epw right-labled: https://search.r-project.org/CRAN/refmans/eplusr/html/Epw.html
br.MetObj: def __init__(self, tmydata, metadata, label='right')

MetObj init can also handle label='center' but then ads satellite data needs to
be modified by taking mean of DHI, GHI,... e.g.
DHI(12:00, center) = (DHI(11:30-12:00) + DHI(12:00-12:30))/2
"""

import datetime as dt
from typing import Literal
from pvlib import location
import pytz

# TODO test other location regarding 30min shift


class Simulation:
    sim_name = 'APV_Floating'  # also used as first part of the .oct file name

    # ground
    ground_albedo = 0.25  # grass

    # speed up options

    # Spatial resolution between sensors
    spatial_resolution = 0.1  # 0.15  # [m]
    # ray tracing accuracy used in br.analysisObj.analysis()
    ray_tracing_accuracy = 'low'  # 'high' does not improve accuracy much but
    # sim time is increased by x3-x4
    use_multi_processing = True
    scan_target: Literal['ground', 'module'] = 'ground'

    # location
    apv_location = location.Location(
        50.86351, 6.52946, altitude=123, tz='Europe/Berlin',
        name='Morchenich')

    # time settings (as local time of the timezone defined in apv_location.tz)
    # currently only as typical meterological year (TMY) = mean over 2005-2020
    sim_date_time = '06-15_11h'  # used as second part of the .oct file name
    time_step = '30minute'  # also possible: '15minute', '1hour'
    # if irradiance_data_source == 'ADS_satellite': dhi and dni values are
    # averaged from sim_date_time-time_step until sim_date_time+time_step
    # (center labeled)
    # and sunposition for gendaylit is also at the sim_date_time

    irradiance_data_source: Literal['EPW', 'ADS_satellite'] = 'ADS_satellite'

    # sky generation type:'gendaylit' or 'gencumsky'
    sky_gen_mode: Literal['gendaylit', 'gencumsky'] = 'gendaylit'

    # needed for sky_gen_mode = 'gencumsky':
    # Insert start date of the year as [month,day,hour]
    startdt = '1-1_0h'
    # Insert end date of year as [month,day,hour]
    enddt = '1-1_23h'

    cm_unit: Literal['Irradiance', 'PAR', 'Shadow-Depth'] = 'Irradiance'
