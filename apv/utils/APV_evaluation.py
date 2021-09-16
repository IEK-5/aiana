''' Uses PVlib to forecast energy yield according to system settings.
'''
# #
from logging import error
import sys
import apv
import apv.settings.user_pathes as user_pathes
from apv.settings.apv_systems import Default as APV_SystSettings
from apv.resources import pv_modules
import apv.utils
import apv.settings.user_pathes as UserPaths
from apv.utils import files_interface as fi
from apv.settings.simulation import Simulation
from datetime import datetime as dt
import os
import pandas as pd
from pathlib import Path
from pandas.core.frame import DataFrame
import pvlib
import numpy as np
import pvfactors


# #
class Evaluate_APV:
    """
    Attributes:
        simSettings (apv.settings.simulation.Simulation):
        simulation settings object
        --------
        met_data(bifacial_radiance.MetObj): meterologic data object
        --------

    """
    # TODO ADD Bifacial factor
    # TODO ADD E\W configuration
    # TODO ADD create file and Dataframe

    def __init__(
            self,
            SimSettings=apv.settings.simulation.Simulation(),
            APV_SystSettings=apv.settings.apv_systems.Default(),
            debug_mode=False
    ):
        self.SimSettings: apv.settings.simulation.Simulation = SimSettings
        self.APV_SystSettings: apv.settings.apv_systems.Default = \
            APV_SystSettings

        self.debug_mode = debug_mode
        # self.create_oct_file = create_oct_file

        self.df_energy_results = pd.DataFrame()
        self.csv_file_name = str()

    def evaluate_APV(self):
        # Adjust settings
        self.APV_SystSettings = apv.utils.settings_adjuster.adjust_settings(
            self.APV_SystSettings)
        # read EPW data from bifacial radiance files
        epw = UserPaths.bifacial_radiance_files_folder / Path('EPWs/')
        for file in os.listdir(epw):
            if file.endswith(".epw"):
                epw = os.path.join(UserPaths.bifacial_radiance_files_folder,
                                   'EPWs/', file)

        (self.tmydata, self.metadata) = pvlib.iotools.read_epw(
            epw, coerce_year=2001)
        self.tmydata.index = self.tmydata.index+pd.Timedelta(hours=1)

        # Create results folder
        e_path = UserPaths.results_folder / Path('Evaluation/')
        fi.make_dirs_if_not_there(e_path)
        # Create csv collection file if not thereb
        E_df = pd.DataFrame({})

        if self.SimSettings.sky_gen_mode == 'gendaylit':
            sim_time = dt.strptime(self.SimSettings.sim_date_time, '%m-%d_%Hh')
            time = pd.date_range(start=sim_time, end=sim_time, freq='1h')
            time.tz_localize(self.SimSettings.apv_location.tz)
            timeindex = apv.utils.time.get_hour_of_year(
                self.SimSettings.sim_date_time)
            energy = estimate_energy(
                SimSettings=self.SimSettings,
                APV_SystSettings=self.APV_SystSettings, time=time,
                timeindex=timeindex,
                tmydata=self.tmydata)
        else:
            startdt = dt.strptime(self.SimSettings.startdt, '%m-%d_%Hh')
            enddt = dt.strptime(self.SimSettings.enddt, '%m-%d_%Hh')
            start_index = apv.utils.time.get_hour_of_year(
                self.SimSettings.startdt)
            end_index = apv.utils.time.get_hour_of_year(
                self.SimSettings.enddt)
            time = pd.date_range(start=startdt, end=enddt, freq='1h')
            time.tz_localize(self.SimSettings.apv_location.tz)
            energy = 0
            for t in time:
                for i in np.arange(start_index, end_index+1):
                    energy += estimate_energy(
                        SimSettings=self.SimSettings,
                        APV_SystSettings=self.APV_SystSettings,
                        time=pd.date_range(t, t, freq='1h'),
                        timeindex=i, tmydata=self.tmydata)
            system_energy = energy['p_mp'] \
                * self.APV_SystSettings.sceneDict['nMods'] \
                * self.APV_SystSettings.sceneDict['nRows'] \
                * self.APV_SystSettings.moduleDict['numpanels']
            print(f"### TOTAL ENERGY : {energy['p_mp']} Wh per module ###\n"
                  + f'### TOTAL ENERGY: {system_energy/1000} kWh per system')

            return energy, system_energy


def estimate_energy(SimSettings, APV_SystSettings, time, timeindex, tmydata):

    # read PV module specs
    input_folder = Path.cwd().parent
    input_folder = os.path.abspath(os.path.join(os.path.dirname(
        pv_modules.__file__), 'Sanyo240_moduleSpecs_guestimate.txt'))
    pv_module: pd.Series = pd.read_csv(input_folder, delimiter='\t').T[0]

    sDict = APV_SystSettings.sceneDict
    mDict = APV_SystSettings.moduleDict

    # Solar position
    sol_pos = pvlib.solarposition.get_solarposition(
        time=time,
        temperature=tmydata.temp_air.iloc[timeindex],
        latitude=SimSettings.apv_location.latitude,
        longitude=SimSettings.apv_location.longitude,
        altitude=SimSettings.apv_location.altitude,
        method='nrel_numpy')

    # DNI Extraterrestrial from Day_of_year
    dni_extra = pvlib.irradiance.get_extra_radiation(time)

    # Calculate relative airmass
    air_mass = pvlib.atmosphere.get_relative_airmass(
        sol_pos['apparent_zenith'])

    # Calculate pressure
    air_press = pvlib.atmosphere.alt2pres(SimSettings.apv_location.altitude)

    # Calculate absolute (corrected) airmass
    air_mass_abs = pvlib.atmosphere.get_absolute_airmass(air_mass, air_press)

    # Angle of Incidence
    aoi = pvlib.irradiance.aoi(
        surface_tilt=sDict['tilt'], surface_azimuth=sDict['azimuth'],
        solar_zenith=sol_pos['apparent_zenith'],
        solar_azimuth=sol_pos['azimuth']
    )
    # Plane of Array (POA) Irradiation
    total_irr = pvlib.irradiance.get_total_irradiance(
        surface_tilt=sDict['tilt'],
        surface_azimuth=sDict['azimuth'],
        solar_zenith=sol_pos['apparent_zenith'],
        solar_azimuth=sol_pos['azimuth'],
        dni=tmydata.dni.iloc[timeindex], ghi=tmydata.ghi.iloc[timeindex],
        dhi=tmydata.dhi.iloc[timeindex], dni_extra=dni_extra,
        model='isotropic')

    # POA for bifacial
    # gcr = mDict['y']*mDict['numpanels']/sDict['pitch']
    # pvrow_width = mDict['x']*sDict['nMods'] + \
    # mDict['xgap']*(sDict['nMods']-1)
    # total_irr2 = pvlib.bifacial.pvfactors_timeseries(
    #     solar_azimuth=sol_pos['azimuth'],
    #     solar_zenith=sol_pos['apparent_zenith'],
    #     surface_azimuth=sDict['azimuth'], axis_azimuth=0,
    #     surface_tilt=sDict['tilt'], timestamps=time,
    #     dni=tmydata.dni.iloc[timeindex], dhi=tmydata.dhi.iloc[timeindex],
    #     gcr=gcr, pvrow_height=sDict['hub_height'], pvrow_width=pvrow_width,
    #     albedo=SimSettings.ground_albedo)

    # print(f'#### Bifacial POA Irradiance \n {total_irr2}')

    # PV cell temperature
    temperature_model_parameters = pvlib.temperature\
        .TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    tcell = pvlib.temperature.sapm_cell(
        total_irr['poa_global'],
        temp_air=tmydata.temp_air.iloc[timeindex],
        wind_speed=tmydata.wind_speed.iloc[timeindex],
        **temperature_model_parameters)

    # Effective Irradiation on array
    effective_irr = pvlib.pvsystem.sapm_effective_irradiance(
        total_irr['poa_direct'], total_irr['poa_diffuse'],
        air_mass_abs, aoi, pv_module)

    # Energy generated
    dc = pvlib.pvsystem.sapm(effective_irr, tcell, pv_module)
    total_energy = dc.sum()
    # TODO define inverter
    # ac = pvlib.inverter.sandia(dc['v_mp'], dc['p_mp'], inverter)

    if APV_SystSettings.module_form == 'cell_level_checker_board':
        total_energy = total_energy/2

    return total_energy
