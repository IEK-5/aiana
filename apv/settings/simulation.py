
import datetime as dt
from typing import Literal
from pvlib import location


class Simulation:
    sim_name = 'APV_Floating'  # also used as first part of the .oct file name

    # ground
    ground_albedo = 0.25  # grass

    # speed up options

    # Spatial resolution between sensors
    spatial_resolution = 5  # 0.15  # [m]
    # ray tracing accuracy used in br.analysisObj.analysis()
    ray_tracing_accuracy = 'low'  # 'high' does not improve accuracy much but
    # sim time is increased by x3-x4
    use_multi_processing = True
    only_ground_scan = True  # if False the backscan will be implemented too

    # time settings
    sim_date_time = '06-15_11h'  # used as second part of the .oct file name

    # location
    apv_location = location.Location(
        50.86351, 6.52946, altitude=123, tz='Europe/Berlin',
        name='Morchenich')

    # sky generation type:'gendaylit' or 'gencumsky'
    sky_gen_mode: Literal['gendaylit', 'gencumsky'] = 'gendaylit'

    # needed for sky_gen_mode = 'gencumsky':
    # Insert start date of the year as [month,day,hour]
    startdt = [6, 1, 0]
    # Insert end date of year as [month,day,hour]
    enddt = [6, 1, 23]
