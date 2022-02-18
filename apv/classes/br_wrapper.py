"""
klassen sollen faul sein
@property statt im init einlesen

dann kann man evt auch auf weather_data übergabe verzichten und

evt. multiple inherence für br_wrapper nutzen mit gleichen argumenten (nur settings)

dann querverweis so, dass plotter in der vererbungskette am ende kommt, dann kennt er auch xfield über oct_file_creator



Ziel: alles modular: oct_file erstellung und ansehen, simulieren, evaluieren,
df ausgeben lassen, plotten,
soll alles unabhängig von einander genutzt werden können.
daher: dataframes werden immer neu von der platte eingelesen,
(evt. optional als default df=None übergeben und wenn =None, dann einlesen vom
standard ort)
damit sie nicht neu erstellt werden müssen.
Falls nicht vorhanden -> print warning


instanziieren der main klasse (br_wrapper) soll schnell gehen und den
gruppierten settings input direkt an die hilfsklassen weiter leiten,
sodass die methoden der hilfsklassen automatisch mit den gleichen settings
arbeiten können.

Weitergereicht werden DFs nur dann, wenn
Zwischenstände nicht auf der platte gespeichert werden sollen. Solche methoden
sollten evt. dann nur in utils kommen (statisch).




uses the other classes to input settings and call from outside:

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


from apv.classes.evaluator import Evaluator
from apv.classes.oct_file_creator import OctFileCreator
from apv.classes.plotter import Plotter
from apv.classes.simulator import Simulator
from apv.utils import files_interface as fi
from apv.classes.weather_data import WeatherData
from apv.classes.util_classes.sim_datetime import SimDT

import bifacial_radiance as br
from typing import Literal
import numpy as np
import pandas as pd
import sys
from pathlib import Path
from apv.classes.util_classes.settings_grouper import Settings


class BR_Wrapper():

    settings: Settings

    def __init__(self, settings: Settings, weatherData=None):
        self.settings = settings
        self.settings.set_names_and_paths()

        if weatherData is None:
            self.weatherData = WeatherData(self.settings)
        else:
            self.weatherData = weatherData

        self.simDT = SimDT(self.settings.sim)

        self.octFileObj = OctFileCreator(
            settings=self.settings, weatherData=self.weatherData
        )
        self.simulatorObj = Simulator(self.settings)

        self.evaluatorObj = Evaluator(self.settings, self.weatherData)

        self.octFileObj.ghObj.x_field
        self.plotterObj = Plotter(self.settings)

    def create_oct_file(self):
        self.octFileObj.create_oct_file()

    def simulate(self):
        """        self.frontscan, self.backscan = self.analObj.moduleAnalysis(
            scene=self.scene, sensorsy=sensorsy)
        scan_dicts{'front': frontscan}"""

        self.simulatorObj.run_raytracing_simulation()

    def plot_ground_heatmap(self):

        ticklabels_skip_count_number = int(
            round(self.octFileObj.ghObj.x_field, 0)
            / (8*self.settings.sim.spatial_resolution))
        if ticklabels_skip_count_number < 2:
            ticklabels_skip_count_number = "auto"

        self.plotterObj.ground_heatmap(
            ticklabels_skip_count_number=ticklabels_skip_count_number)
    # def run_raytracing_simulation(self):

    # def plot_ground_heatmap(self):
