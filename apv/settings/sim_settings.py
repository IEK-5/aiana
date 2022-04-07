# #
from pathlib import Path
from typing import Literal
from pvlib import location


class Simulation:
    """all settings can also be overwritten in a working file
    as long as a br_wrapperObj is initializated afterwards.
    See system_studies/apv_main.py for a simple example"""

    def __init__(self):
        self.study_name: str = 'APV_Floating'

        self.results_subfolder: Path = Path('test')

        self.ground_albedo = 0.25  # grass

        self.spatial_resolution = 0.1  # [m]
        # distance between virtual radiation sensors

        self.sim_year: int or Literal['TMY'] = 'TMY'  # or e.g. 2020
        # TMY = typical meterological year; here: mean data from 2005 to 2021

        self.use_typDay_perMonth_for_irradianceCalculation = True  # for dni, dhi, ghi

        self.TMY_irradiance_aggfunc: Literal['min', 'mean', 'max'] = 'mean'
        # also used as aggregation function for satelite watherdata pivoting to TMY
        # min: extreme cloudy day, max: sunny day with distant high bright clouds

        self.use_CPU_multi_processing = True
        # if True, single lines of the scan area will be passed to a job pool
        # worked off by the cpu cores in parallel

        # Accelerad settings ####################
        # need to be installed first https://nljones.github.io/Accelerad/index.html
        self.use_acceleradRT_view = False  # real time scene navigation and viewing
        self.use_accelerad_GPU_processing = False  # GPU paralellization, all line scans
        # at once. GPU multiprocessing is not compatible with CPU multiprocessing
        # and will thus ignore use_CPU_multi_processing setting, if True

        # location
        self.apv_location = location.Location(
            50.86351, 6.52946, altitude=123, tz='Europe/Berlin', name='Morchenich'
        )

        # time settings (right labled with interval = time_step_in_minutes s.below)
        # and as local time of the timezone defined in apv_location.tz
        # currently only as typical meterological year
        self.sim_date_time: str = '06-15_12:00'  # month-day_time
        # will be also used as second part of the .oct file name

        self.time_step_in_minutes: int = 60
        # only prime-factos of 60! (1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60)

        """NOTE Important info
        ghi and dhi are taken from an observation period ranging
        from [sim_date_time - time_step_in_minutes] until [sim_date_time]
        and the sunposition is calculated at a time in between.
        e.g. a sim_date_time = 12h will at the moment result in irradiation data
        11-12h and sol position 11:30h
        (bifacial radiance uses also right-labled timestamps)
        epw also right-labled:
        https://search.r-project.org/CRAN/refmans/eplusr/html/Epw.html
        br.MetObj: def __init__(self, tmydata, metadata, label='right')
        """

        # quantity on the color map of the heatmap of the results (output)
        self.cm_quantity: Literal[
            'radiation', 'PAR', 'shadow_depth', 'DLI'] = 'radiation'
        # !!! NOTE 'DLI' is only for daily cumulative data, no single timesteps

        self.plot_dpi: int = 500  # dots per inch in the result heatmaps

        self.plot_title_components: list = ['weather', 'datetime']
        # all options: ['weather', 'module_form', 'resolution',
        #                'position', 'agg_func', 'datetime']
        self.scan_position: Literal['north', 'center', 'south', 'east'] = 'south'
        # to be used in scan field shifting, to shift scanned area within a system
        self.plots_shifts_xy = {'north': [0, 1], 'center': [0, 0],
                                'south': [0, -1], 'east': [3, 0]}

        ##################
        # less important / not fully implemented at the moment
        self.scan_target: Literal['ground', 'module'] = 'ground'
        # TODO for module east west see br tutorial 19

        # sky generation type:
        self.sky_gen_mode: Literal['gendaylit'
                                   # , 'gencumsky'  # not included at the moment
                                   ] = 'gendaylit'

        # needed for sky_gen_mode = 'gencumsky':
        # Insert start date of the year as [month,day,hour]
        self.startdt = '1-1_0:00'
        # Insert end date of year as [month,day,hour]
        self.enddt = '1-1_23:00'  # inclusive ([:end+1])

        # cumulative is done at the moment via for loop of single moments
        self.cumulative: bool = False

        self.irradiance_data_source: Literal['EPW', 'ADS_satellite'] = 'ADS_satellite'
        # >>> we dont use EPW anymore


class SimSettings_ForTesting(Simulation):
    def __init__(self):
        super().__init__()
        self.sim_date_time = '06-15_12:00'
        self.spatial_resolution = 1
        self.use_typDay_perMonth_for_irradianceCalculation = False
        self.use_CPU_multi_processing = False
        self.use_accelerad_GPU_processing = True
        self.use_acceleradRT_view = True
