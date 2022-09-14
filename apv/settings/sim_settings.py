# #
from typing import Literal
from pvlib import location


class Simulation:
    """all settings can also be overwritten in a working file
    as long as a br_wrapperObj is initializated afterwards.
    See system_studies/apv_main.py for a simple example"""

    def __init__(self):

        self.study_name: str = 'myStudy'  # will be used as sub folder for
        # all results of the current study
        # this attribute is not placed in user_paths.py to allow for changing
        # it within a working file from outside via settings.sim.study_name=...
        # (Settings._paths is overwritten by user_paths.py default values and
        # settings.sim is not).

        self.sub_study_name: str = 'mySubStudy'  # will be added as prefix
        # to cumulative plots and their corresponding data sub folders

        self.spatial_resolution = 0.1  # [m]
        # distance between virtual radiation sensors
        self.ground_albedo = 0.24  # grass

        # time settings (right labled with interval = time_step_in_minutes s.below)
        self.sim_year: Literal['TMY'] = 'TMY'  # or e.g. 2020
        # TMY = typical meterological year; here: mean data from 2005 to 2021

        self.month: int = 6
        self.day: int = 15

        # hours as local time of the timezone defined in apv_location.tz
        self.hours: list = list(range(3, 24))
        # GHI will be summed for all hours given in this list
        # (including minutes) to calculate the irradiation,
        # cumulative shadow depth and DLI
        self.hour_for_sceneInspection = 14  # noon, good to check azimuth

        self.time_step_in_minutes: int = 60  # <= 60 and
        # only prime-factos of 60! (1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60)

        # sky generation type:
        self.sky_gen_mode: Literal['gendaylit'
                                   # , 'gencumsky'  # not included at the moment
                                   ] = 'gendaylit'

        """NOTE Important info
        ghi and dhi are taken from an observation period ranging
        from [sim_date_time - time_step_in_minutes] until [sim_date_time]
        and the sunposition is calculated at a time in between.
        e.g. a hours = [12] and time_step_in_minutes = 60
        will at the moment result in irradiation data 11-12h and sol position
        from 11:30h (bifacial radiance uses also right-labled timestamps)
        epw also right-labled:
        https://search.r-project.org/CRAN/refmans/eplusr/html/Epw.html
        br.MetObj: def __init__(self, tmydata, metadata, label='right')
        """

        self.use_typDay_perMonth_for_irradianceCalculation = True
        # for dni, dhi, ghi True to compare mean of month to mean of month
        # and not to data of 15th

        self.use_CPU_multi_processing = True
        # if True, single lines of the scan area will be passed to a job pool
        # worked off by the cpu cores in parallel

        # ray tracing settings, from:
        # http://designbuilder.co.uk/helpv3.0/Content/Daylighting%20Calculation%20Options.htm#Ambient4
        self.rtraceAccuracyDict = {
            'std': {'ab': 2, 'aa': .1, 'ar': 256, 'ad': 1024, 'as': 256},  # 4.3 sec
            'good_no_interp': {'ab': 2, 'aa': 0, 'ar': 256, 'ad': 1024, 'as': 512},  # 4.6 sec
            'accurate': {'ab': 2, 'aa': .2, 'ar': 512, 'ad': 2048, 'as': 1024},  # 4.8 sec
            'acc_no_interp': {'ab': 2, 'aa': 0, 'ar': 512, 'ad': 2048, 'as': 1024},  # 8.4 sec
            'hq':      {'ab': 3, 'aa': .1, 'ar': 1024, 'ad': 4096, 'as': 2048}  # 10 sec
        }
        # NOTE hq results in really dark artefacts around posts
        # std in smaler dots
        # without interpolation: no artefacts
        self.rtraceAccuracy: Literal[
            'std', 'good_no_interp', 'accurate', 'acc_no_interp', 'hq'] \
            = 'good_no_interp'

        # Accelerad settings ####################
        # need to be installed first https://nljones.github.io/Accelerad/index.html
        self.use_accelerad_GPU_processing = False  # GPU paralellization, all line scans
        # at once. GPU multiprocessing is not compatible with CPU multiprocessing
        # and will thus ignore use_CPU_multi_processing setting, if True

        # location
        self.apv_location = location.Location(
            50.86351, 6.52946, altitude=123, tz='Europe/Berlin', name='Morschenich'
        )

        # quantity on the color map of the heatmap of the results (output)
        self.cm_quantity: Literal[
            'radiation', 'PAR', 'shadow_depth', 'DLI'] = 'radiation'
        # !!! NOTE 'DLI' is only for daily cumulative data, no single timesteps

        self.for_shadowDepths_compare_GGI_to: Literal[  # GGI =Global ground ir.
            'clearsky_GHI', 'GHI_as_TMY_aggfunc'] = 'GHI_as_TMY_aggfunc'

        self.TMY_irradiance_aggfunc: Literal['min', 'mean', 'max'] = 'mean'
        # also used as aggregation function for satelite watherdata pivoting to TMY
        # min: extreme cloudy day, max: sunny day with distant high bright clouds

        self.plot_dpi: int = 300  # dots per inch in the result heatmaps

        self.plot_title_components: list = ['weather', 'datetime']
        # all options: ['weather', 'module_form', 'resolution',
        #                'position', 'agg_func', 'datetime']

        # for the radiance sensors, zstart is where a radiance sensor vector starts
        # it is looking downwards with orientation 0 0 -1 and will read the
        # irradiance (?) of the surface the ray will hit first. To measure
        # something being heigher than the ground with z = 0, we need to add an
        # object with a surface (a scan_area or a plant...)

        self.RadSensors_z_params: dict = {'zstart': 0.1,
                                          'zinc': 0,  # not yet implemented,
                                          'Nz': 1}  # not yet implemented
        # multiple z,x,y doesnt make sense anyways as object is needed
        # to recieve the light
        self.RadSensors_to_scan_area_distance_z = 0.1

        self.north_arrow_xy_posi = (1.6, 1.2)  # x, y within heat maps

        ##################
        # less important / not fully implemented or obsolete at the moment

        self.scan_position: Literal['north', 'center', 'south', 'east'] = 'south'
        # to be used in scan field shifting, to shift scanned area within a system
        self.plots_shifts_xy = {'north': [0, 1], 'center': [0, 0],
                                'south': [0, -1], 'east': [3, 0]}

        self.scan_target: Literal['ground', 'module'] = 'ground'
        # TODO for module east west see br tutorial 19

        # cumulative is done at the moment via merging single time step results
        # self.cumulative: bool = False

        self.irradiance_data_source: Literal['EPW', 'ADS_satellite'] = 'ADS_satellite'
        # >>> we dont use EPW anymore


class SimSettings_ForTesting(Simulation):
    def __init__(self):
        super().__init__()
        self.spatial_resolution = 1
        self.use_typDay_perMonth_for_irradianceCalculation = False
        self.use_CPU_multi_processing = False
        self.use_accelerad_GPU_processing = True
