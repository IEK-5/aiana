from typing import Literal
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
    a settings objevt (for simulation, APV system, names and pathes - all
    grouped by util_classes.setings_grouper) to the other classes/objects
    fulfilling the following study steps:

    1. OctFileHandler to create/view octfiles
        (the oct-format is needed for Radiance simulations and contains the
        scene information about the geometries, materials and sky.
        The OctFileHandler takes as additional input two util_classes-objects:
        - a weatherData-object containing the correct irradiance and sun
            position based on the time settings in sim_settings, and
        - a geometries_handler-object, which creates based on the apv_system
            settings rad-files (Radiance text file format for geometries)
    2. simulatorObj to simulate (tabular results creation), which needs
        - the settings for sim input and output file names and pathes,
        - the above mentioned geometries_handler-object for the scan positions
    3. evaluatorObj to evaluate(tabular results processing), which needs
        - the settings for file names and pathes,
        - the weatherData-object to update from outside, based on the time in
          the settings, the reference GHI for a fast (also in loops)
          shadow depth calculation
    4. plotterObj for plotting the results, which needs
        - the settings for file names and pathes, title, colormap unit, ...
        - the geometries_handler-object to (try to) avoid axis tick labels
          overlapping, buy taking scan area size and resolution into account
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
        self._init_simulator_evaluator_and_plotter()

    def _init_simulator_evaluator_and_plotter(self):
        """put into a method to allow for calling it again
        after updating the timestep from outside, which affects
        self.settings.names and .paths
        """
        self.simulatorObj = Simulator(self.settings, self.ghObj)
        self.evaluatorObj = Evaluator(self.settings, self.weatherData)
        self.plotterObj = Plotter(self.settings, self.ghObj)

    def create_octfile(
            self, add_groundScanArea: bool = False,
            add_sensor_vis: bool = False,
            add_NorthArrow: bool = False,
            update_sky_only: bool = False):
        """for simulation preperation in two steps:
            # 1 optional create scene without sky,
            # 2 add sky
        (set update_sky_only=True to skip step #1)
        reduced large scene creation from 40 to 20 seconds.

        WARNING: add_groundScanArea is needed for different scan startz
        but the ground albedo won't be used this way. #TODO)
        """
        if update_sky_only:
            pass
        else:
            self.octFileObj.create_octfile_without_sky(
                add_groundScanArea, add_sensor_vis, add_NorthArrow)
        self.octFileObj.add_sky_to_octfile()

    def create_and_view_octfile_for_SceneInspection(
            self, add_groundScanArea: bool = True,
            add_sensor_vis: bool = True,
            add_NorthArrow: bool = True,
            view_name: Literal['total', 'close_up', 'top_down'] = 'total'):
        """for scene inspection: add ground scan area and north arrow
        visualiation, switch to parallel view for top down, which allows for
        more easy checking of a post-to-post scan area unit cell placement.

        view_name: Literal['total', 'close_up', 'top_down']
        """
        self.create_octfile(
            add_groundScanArea, add_sensor_vis, add_NorthArrow)
        view_type = 'parallel' if view_name == 'top_down' else 'perspective'
        self.octFileObj.view_octfile(view_name=view_name, view_type=view_type)

    def update_timeStep_and_sky(self, settings: Settings):
        """refresh names, paths, sim settings, sky dome, and other objects
        allowing that APV geometry does not have to be build again.
        """
        self.settings = settings
        self.settings.set_names_and_paths()
        self.weatherData.set_dhi_dni_ghi_and_sunpos_to_simDT(
            SimDT(self.settings.sim))
        vis_added = self.octFileObj.ResultsFalsifyingVisualisationsAdded
        self.octFileObj = OctFileHandler(
            self.settings, self.weatherData, self.ghObj
        )
        # since octFileObj init sets vis_added to False:
        self.octFileObj.ResultsFalsifyingVisualisationsAdded = vis_added
        self.octFileObj.add_sky_to_octfile()
        self._init_simulator_evaluator_and_plotter()

    def simulate_and_evaluate(self):
        if self.octFileObj.ResultsFalsifyingVisualisationsAdded:
            print('Warning: Creating octfile again without scanArea',
                  'or North_arrow as objects as these would falsify',
                  'the simulation results. To save time, create octfile',
                  'without visualisations of scanArea or north arrow added.')
            # NOTE "falsify", as the edge of the scanArea object will
            # result in darker lines in the edge of the irradiation heatmaps.
            self.create_octfile()
        self.simulatorObj.run_raytracing_simulation()
        self.evaluatorObj.rename_and_add_result_columns()
