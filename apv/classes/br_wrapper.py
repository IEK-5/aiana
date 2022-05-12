from apv.classes.util_classes.settings_grouper import Settings
from apv.classes.util_classes.geometries_handler import GeometriesHandler
from apv.classes.util_classes.sim_datetime import SimDT
from apv.classes.weather_data import WeatherData
from apv.classes.oct_file_handler import OctFileHandler
from apv.classes.simulator import Simulator
from apv.classes.evaluator import Evaluator
from apv.classes.plotter import Plotter


class BR_Wrapper():

    """This is the core class, which is linking all other classes. It passes
    the settings to the other classes/objects, which were grouped based on
    these study steps:

    - create/view octfile via the octFileObj class
        (the oct-format is needed for Radiance simulation and contains the
        scene infos such as geometries and sky information.
        an octFileObj takes as additional input two util_classes-objects:
        a weatherData-object containing the correct irradiance and sun position
        based on the time set in settings/simulation,
        and a geometries_handler-object, which creates the rad-files, which
        hold the geometry information in the Radiance text file format.)
    - simulate via simulatorObj (tabular results creation/saving)
    - evaluate via evaluatorObj (tabular results processing/saving)
    - plot via plotterObj
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.settings.set_names_and_paths()
        # print('csv_file exists: ', self.settings.paths.csv_file_path.exists())

        self.weatherData = WeatherData(self.settings)
        self.ghObj = GeometriesHandler(self.settings,  # self.debug_mode=True
                                       )
        self.octFileObj = OctFileHandler(
            self.settings, self.weatherData, self.ghObj,
            # self.debug_mode=True
        )
        self._init_simulator_evaluator_plotter()

    def _init_simulator_evaluator_plotter(self):
        self.simulatorObj = Simulator(self.settings, self.ghObj)
        self.evaluatorObj = Evaluator(self.settings, self.weatherData)
        self.plotterObj = Plotter(self.settings, self.ghObj)

    def create_octfile(self, add_groundScanArea=False,
                       add_NorthArrow=False, update_sky_only=False):
        if not update_sky_only:
            self.octFileObj.create_octfile_without_sky(
                add_groundScanArea, add_NorthArrow)
        self.octFileObj.add_sky_to_octfile()

    def create_and_view_octfile(self, add_groundScanArea=True,
                                add_NorthArrow=False, view_name='total'):
        self.create_octfile(add_groundScanArea, add_NorthArrow)
        view_type = 'parallel' if view_name == 'top_down' else 'perspective'
        self.octFileObj.view_octfile(view_name=view_name, view_type=view_type)

    def update_timeStep(self, settings: Settings):
        """refresh names, paths, sim settings, sky dome, and other objects
        allowing that APV geometry does not have to be build again.
        """
        self.settings = settings
        self.settings.set_names_and_paths()
        self.weatherData.set_dhi_dni_ghi_and_sunpos_to_simDT(
            SimDT(self.settings.sim))
        self.octFileObj = OctFileHandler(
            self.settings, self.weatherData, self.ghObj
        )
        self.octFileObj.add_sky_to_octfile()
        self._init_simulator_evaluator_plotter()

    def simulate_and_evaluate(self):
        if self.octFileObj.groundScanArea_added:
            print('Creating octfile again without groundScanArea as object ',
                  'as this object would falsify the simulation results.')
            # NOTE falsify, as the edge of the groundScanArea object will
            # result in darker lines in the edge of the irradiation heatmaps.
            self.create_octfile()

        self.simulatorObj.run_raytracing_simulation()
        self.evaluatorObj.rename_and_add_result_columns()
