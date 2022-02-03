# #
from typing import Literal
from pvlib import location


class Simulation:
    sim_name = 'APV_Floating'  # also used as first part of the
    # Radiance scene file name (.oct) and the output files

    ground_albedo = 0.25  # grass

    # Spatial resolution between virtual radiation sensors
    spatial_resolution = 0.1  # [m]

    sim_year: int or Literal['TMY'] = 'TMY'  # or e.g. 2020
    # TMY = typical meterological year; here: mean data from 2005 to 2020

    TMY_irradiance_aggfunc: Literal['min', 'mean', 'max'] = 'mean'
    # also used as aggregation function for satelite watherdata pivoting to TMY
    # min: extreme cloudy day, max: complete could-free sunny day

    use_multi_processing = True

    # location
    apv_location = location.Location(
        50.86351, 6.52946, altitude=123, tz='Europe/Berlin',
        name='Morchenich')

    # time settings (as local time of the timezone defined in apv_location.tz)
    # currently only as typical meterological year

    use_typDay_perMonth_for_shadowDepthCalculation = False

    sim_date_time = '06-15_20:00'  # used as second part of the .oct file name
    time_step_in_minutes: int = 60  # only 1,2,3,6,10,12,15,20,30,60,120

    """Important info
    # at the moment ghi and dhi is taken from an observation period ranging
    # from sim_date_time - time_step_in_minutes until sim_date_time
    # and the sunposition is taken at
    # sim_date_time - int(time_step_in_minutes/2)
    so a sim_date_time = 12h will at the moment result in irradiation data
    11-12h and sol position 11:30
    (bifacial radiance uses right-labled timestamps and does it this way)
    epw right-labled:
    https://search.r-project.org/CRAN/refmans/eplusr/html/Epw.html
    br.MetObj: def __init__(self, tmydata, metadata, label='right')

    br.MetObj init can also handle label='center' but then ads satellite data
    needs to be modified by taking mean of DHI, GHI,... e.g.
    DHI(12:00, center) = (DHI(11:30-12:00) + DHI(12:00-12:30))/2

    # so.. TODO maybe nice way:
    # if irradiance_data_source == 'ADS_satellite': dhi and dni values are
    # averaged from sim_date_time-time_step until sim_date_time+time_step
    # (center labeled)
    # and sunposition for gendaylit is taken at the sim_date_time
    """

    # quantity on the color map of the heatmap of the results (output)
    cm_quantity: Literal[
        'radiation', 'PAR', 'shadow_depth', 'DLI'] = 'radiation'

    ##################
    # less important / not fully implemented at the moment
    scan_target: Literal['ground', 'module'] = 'ground'
    # sky generation type:
    sky_gen_mode: Literal['gendaylit'
                          # , 'gencumsky'  # not included at the moment
                          ] = 'gendaylit'

    # needed for sky_gen_mode = 'gencumsky':
    # Insert start date of the year as [month,day,hour]
    startdt = '1-1_0:00'
    # Insert end date of year as [month,day,hour]
    enddt = '1-1_23:00'  # inclusive ([:end+1])

    # cumulative is done at the moment via for loop of single moments
    cumulative: bool = False
    # ray tracing accuracy used in br.analysisObj.analysis()
    ray_tracing_accuracy = 'low'  # 'high' does not improve accuracy much but
    # increases simtime by 3x-4x

    irradiance_data_source: Literal['EPW', 'ADS_satellite'] = 'ADS_satellite'
    # >>> we dont use EPW anymore, bad data
