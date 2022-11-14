""" This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>."""
import os
import pandas as pd
from aiana.utils import files_interface as fi

from typing import Literal
from aiana.classes.util_classes.settings_handler import Settings
from aiana.classes.rad_txt_related.geometries_handler import GeometriesHandler
from aiana.classes.weather_data import WeatherData
from aiana.classes.oct_file_handler import OctFileHandler
from aiana.classes.simulator import Simulator
from aiana.classes.evaluator import Evaluator
from aiana.classes.plotter import Plotter


class AianaMain():
    # sim time/timespan in plot title
    # TODO automatic plotting with equal color bar per day

    """This is the core class, which is linking all other classes. It passes
    a settings objevt (for simulation, APV system, names and pathes - all
    grouped by util_classes.setings_grouper) to the other classes/objects
    fulfilling the following study steps:

    1. OctFileHandler to create/view octfiles
        (the oct-format is needed for Radiance simulations and contains the
        scene information about the geometries, materials and sky.
        The OctFileHandler takes besides the settings as input two
        util_classes-objects:
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
        self.settings.update_sim_dt_and_paths()

        self.weatherData = WeatherData(self.settings)
        self.ghObj = GeometriesHandler(self.settings,  # self.debug_mode=True
                                       )
        self.octFileObj = OctFileHandler(
            self.settings, self.weatherData, self.ghObj,
            # self.debug_mode=True
        )
        self.update_simTime()
        self._init_simulator_evaluator_and_plotter()

    def create_and_view_octfile_for_SceneInspection(
            self, add_groundScanArea: bool = True,
            add_sensor_vis: bool = True,
            add_NorthArrow: bool = True,
            view_name: Literal['total', 'close_up', 'top_down'] = 'total'):
        """
        opens the oct file in the viewer. If Accererad is used, you can
        navigate as following:

        rotate = holding right-click and move mouse
        pan = holding shift+right-click and move mouse
        zoom in/out = mousewheel up/down

        for scene inspection: add ground scan area and north arrow
        visualiation, switch to parallel view for top down, which allows for
        more easy checking of a post-to-post scan area unit cell placement.

        view_name: Literal['total', 'close_up', 'top_down']

        WARNING: add_groundScanArea is needed for different scan startz
        but the ground albedo won't be used this way. #TODO
        """
        self.octFileObj.create_octfile_without_sky(
            add_groundScanArea=add_groundScanArea,
            add_sensor_vis=add_sensor_vis, add_NorthArrow=add_NorthArrow)

        self.update_simTime(hour=self.settings.sim.hour_for_sceneInspection)
        self._update_sky()
        view_type = 'parallel' if view_name == 'top_down' else 'perspective'
        self.octFileObj.view_octfile(view_name=view_name, view_type=view_type)

    def update_simTime(self, **kwargs):
        """
        # updates time settings, pathes, labels, weatherData...

        **kwargs:
        year: int = ..., month: int = ..., day: int = ...,
        hour: int = ..., minute: int = ..., as in dt.replace()
        """
        self.settings.update_sim_dt_and_paths(**kwargs)
        self.weatherData.set_dhi_dni_ghi_and_sunpos_to_simDT(self.settings)

    def simulate_and_evaluate(self, skip_sim_for_existing_results=False,
                              # clear_existing_results=False # for testing to avoid cumulating different settings
                              ):
        # Creating octfile without scanArea or North_arrow as objects as these
        # would falsify the simulation results, since e.g. the edge of the
        # scanArea object would result in darker lines in the edge of the
        # irradiation heatmaps. Sky is added later to save cpu time.
        self.octFileObj.create_octfile_without_sky()

        for loop_to in ["sim", "plot"]:  # for equal colbar all results needed
            if loop_to == "plot" and \
                    self.settings.sim.equal_colBars_for_instantaneous_plots:
                csv_root = self.settings._paths.inst_csv_parent_folder
                csv_files = [csv_root/file for file in os.listdir(csv_root)]
                df_limits = fi.get_min_max_in_several_csv_files(
                    csv_files).round(1)
            else:
                df_limits = None

            for hour in self.settings.sim.hours:
                for minute in range(0, 60, self.settings.sim.time_step_in_minutes):
                    self.update_simTime(hour=hour, minute=minute)
                    # Sun alitude and GHI FILTER ==============================
                    if (self.weatherData.sunalt < 0):
                        print(f'Sun alitude < 0 ({self.weatherData.sunalt}).')
                    elif self.weatherData.ghi < min(
                            self.weatherData.dailyCumulated_ghi * 0.02, 50):
                        print(f'GHI too low ({self.weatherData.ghi} Wh/m²).')
                    # =========================================================
                    elif loop_to == "sim":  # enough light and sim loop
                        res_path = self.settings._paths.inst_csv_file_path
                        if res_path.exists() and skip_sim_for_existing_results:
                            print(f'result {res_path} exists, skipping sim...')
                            # check if evaluated to avoid 'Wm2' key error
                            df_check: pd.DataFrame = fi.df_from_file_or_folder(
                                res_path
                            )
                            if 'Wm2' not in df_check.columns:
                                self.evaluatorObj.evaluate_csv()
                        else:
                            self._update_sky()
                            self._init_simulator_evaluator_and_plotter()
                            self.simulatorObj.run_raytracing_simulation()
                            self.evaluatorObj.evaluate_csv()
                    elif loop_to == "plot":
                        self.plotterObj.ground_heatmap(
                            df_col_limits=df_limits)
        # cumulate
        self.evaluatorObj.cumulate_results()
        self.plotterObj.ground_heatmap(cumulative=True)

    # helpers =============================================================

    def _init_simulator_evaluator_and_plotter(self):
        """put into a method to allow for calling it again
        after updating the time from outside, which affects
        self.settings.names and .paths
        """
        self.simulatorObj = Simulator(self.settings, self.ghObj)
        self.evaluatorObj = Evaluator(self.settings, self.weatherData)
        self.plotterObj = Plotter(self.settings, self.ghObj)

    def _update_sky(self):
        """refresh names, paths, sim settings, sky dome, and other objects
        allowing that APV geometry does not have to be build again,
        if no tracking is involved.

        updating sky only instead of rebuilding geometry as well
        reduced large scene creation from 40 to 20 seconds.
        """

        self.octFileObj = OctFileHandler(
            self.settings, self.weatherData, self.ghObj
        )
        self.octFileObj.add_sky_to_octfile()
