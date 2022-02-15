"""
uses the other classes to input settings and call from outside:

- setup file_names and paths
- make oct file from rad files prepared via geometries_handler class
- view oct file
- simulate
- evaluate
- plot





old:


Called by main.py with the needed parameters to set the neccessary
objects, create scene and run simulation with Bifacial_Radiance according
to presets in settings.py

TODO

---------------------

- module clone does not work anymore...
- aufräumen, dokumentieren, codeinterne TODOs sichten
- apv evaluation angucken und verstehen (Leo)

------------
longterm:
- GPU 28x faster rtrace https://nljones.github.io/Accelerad/index.html
- implement 'module' scan_target ?
- implement era5 data (apv_evaluation: yield & weather_data: solar position)
- add diffusive glass to be used optional in checker board empty slots.
ref: Miskin2019 and
https://www.pv-magazine.com/2020/07/23/special-solar-panels-for-agrivoltaics/

(-bei azi 180°:
wedgeplot x-achse: y-position im field, y-achse: GHI, monat 1-12 untereinander)

- estimate costs of double sized checker boards for same electrical yield with
 improved shadow values and compare to std
- also compare normal sized with double sized checker board shadow maps"

(- gendaylitmxt für kumulativen sky? Aber damit ermittlung von shadow duration
eh nicht möglich...)

"""


from apv.classes.oct_file_creator import OctFileCreator
from apv.utils import plotting
from apv.utils import files_interface as fi
from apv.settings import user_paths
from apv.settings.simulation import Simulation
from apv.settings.apv_systems import Default as SystSettings
from apv.classes.geometries_handler import GeometriesHandler
from apv.classes.weather_data import WeatherData
from apv.classes.APV_evaluation import APV_Evaluation
from apv.classes.util_classes.sim_datetime import SimDT

import bifacial_radiance as br
from typing import Literal
import numpy as np
import pandas as pd
import sys
from pathlib import Path

from apv.utils import radiance_utils


from apv.classes.util_classes.file_name_and_paths_storage import Paths
from apv.classes.util_classes.file_name_and_paths_storage import FileNames
from apv.classes.util_classes.settings_grouper import Settings


class BR_Wrapper:

    ygrid: list[int]
    groundscan: dict
    frontscan: dict
    df_ground_results: pd.DataFrame

    analObj: br.AnalysisObj
    pathS: Paths

    settings: Settings

    def __init__(
            self,
            settings: Settings,
            results_subfolder: Path = None,
            weatherData=None,
            # weather_file=None,  # to optionally skip epw download
            debug_mode=False
    ):
        self.settings = settings

        if weatherData is None:
            self.weatherData = WeatherData(self.settings.sim, debug_mode)
        else:
            self.weatherData = weatherData

        self.evalObj: APV_Evaluation = APV_Evaluation(
            SimSettings=SimSettings,
            APV_SystSettings=self.settings.apv,
            weatherData=self.weatherData
        )

        self.results_subfolder = results_subfolder
        self.debug_mode = debug_mode

        self.simDT = SimDT(self.settings.sim)


        self.octFileCreator = OctFileCreator(debug_mode=True)

    def run_raytracing_simulation(self):

    def plot_ground_heatmap(self):
