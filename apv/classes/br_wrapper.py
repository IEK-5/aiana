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
    its settings input to the other classes/objects, which were grouped based
    on these study steps:

    - create/view octfile via the OctFileHandler class
        (the oct-format is needed for Radiance simulation and contains the
        scene information about the geometries, materials and sky.
        The OctFileHandler takes as additional input two util_classes-objects:
        - a weatherData-object containing the correct irradiance and sun
        position based on the time settings in sim_settings, and
        - a geometries_handler-object, which creates the rad-files, which
        hold the geometry information in the Radiance text file format and
        are input for the oct files)
    - simulate via simulatorObj (tabular results creation)
        -needs settings to know which input files to take and where to save to,
         and geometries_handler-object for the scan positions
    - evaluate via evaluatorObj (tabular results processing)
        -needs settings for file names and pathes,
        -a weatherData-object to update from outside, based on the time in the
        settings, the reference GHI for a fast (also in loops) shadow depth
        calculation
    - plot results via plotterObj
        -needs settings for file names and pathes, title, colormap unit, ...
        -needs geometries_handler-object to (try to) avoid axis tick labels
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
        after updating the timestep from outside, which affects self.settings
        """
        self.simulatorObj = Simulator(self.settings, self.ghObj)
        self.evaluatorObj = Evaluator(self.settings, self.weatherData)
        self.plotterObj = Plotter(self.settings, self.ghObj)

    def create_octfile_for_Simulation(
            self, add_groundScanArea=False, add_sensor_vis=False,
            add_NorthArrow=False, update_sky_only=False):
        """for simulation preperation in two steps:
            #1 optional create scene without sky,
            #2 add sky
        (passing #1 by setting update_sky_only=True
        reduced large scene creation from 40 to 20 seconds.

        WARNING: add_groundScanArea is needed for differenzt scan startz
        but the ground albedo wount be used this way. #TODO)
        """
        if update_sky_only:
            pass
        else:
            self.octFileObj.create_octfile_without_sky(
                add_groundScanArea, add_sensor_vis, add_NorthArrow)
        self.octFileObj.add_sky_to_octfile()

    def create_and_view_octfile_for_SceneInspection(
            self, add_groundScanArea=True, add_sensor_vis=True,
            add_NorthArrow=True, view_name='total'):
        """for scene inspection: add ground scan area and north arrow
        visualiation, switch to parallel view for top down, which allows for
        more easy checking of a post-to-post scan area unit cell placement"""
        self.create_octfile_for_Simulation(
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
            self.create_octfile_for_Simulation()
        self.simulatorObj.run_raytracing_simulation()
        self.evaluatorObj.rename_and_add_result_columns()
