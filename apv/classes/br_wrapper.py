from apv.classes.util_classes.settings_grouper import Settings
from apv.classes.util_classes.geometries_handler import GeometriesHandler
from apv.classes.weather_data import WeatherData
from apv.classes.oct_file_creator import OctFileCreator
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
        print('csv_file exists: ', self.settings.paths.csv_file_path.exists())

        self.weatherData = WeatherData(self.settings)
        self.ghObj = GeometriesHandler(self.settings,  # self.debug_mode=True
                                       )
        self.octFileObj = OctFileCreator(
            self.settings, self.weatherData, self.ghObj,
            # self.debug_mode=True
        )
        self.simulatorObj = Simulator(self.settings, self.ghObj)
        self.evaluatorObj = Evaluator(self.settings, self.weatherData)
        self.plotterObj = Plotter(self.settings, self.ghObj)

    def simulate_and_evaluate(self):
        self.simulatorObj.run_raytracing_simulation()
        self.evaluatorObj.add_time_stamps_PAR_shadowDepth_to_csv_file()
