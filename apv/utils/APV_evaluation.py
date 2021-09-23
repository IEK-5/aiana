''' Uses PVlib to forecast energy yield according to system settings.
'''
# #
import sys
from apv.utils.weather_data import WeatherData
import apv
from apv.resources import pv_modules
import apv.utils
import apv.settings.user_pathes as UserPaths
from apv.utils import files_interface as fi
import os
import pandas as pd
from pathlib import Path
from pandas.core.frame import DataFrame
import pvlib
import numpy as np
# import pvfactors


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
    # TODO ADD E\W configuration in own function

    # TODO Check results with ADS weather file

    def __init__(
            self,
            SimSettings=apv.settings.simulation.Simulation(),
            APV_SystSettings=apv.settings.apv_systems.Default(),
            debug_mode=False
    ):
        self.SimSettings: apv.settings.simulation.Simulation = SimSettings
        self.APV_SystSettings: apv.settings.apv_systems.Default = \
            APV_SystSettings
        self.weatherObj = WeatherData()
        self.debug_mode = debug_mode
        self.df_energy_results = {}
        self.csv_file_name = str()

    def evaluate_APV(self):
        SimSettings = self.SimSettings
        # Adjust settings
        self.APV_SystSettings = apv.utils.settings_adjuster.adjust_settings(
            self.APV_SystSettings)
        # read EPW data from bifacial radiance files
        self.get_weather_data(SimSettings)
        # Create results folder
        eval_res_path = UserPaths.results_folder / Path('Evaluation/')
        fi.make_dirs_if_not_there(eval_res_path)
        # View energy generated on specific date-time
        if SimSettings.sky_gen_mode == 'gendaylit':
            # gendaylit sky not used, but energy for hour will be calculated
            sim_dt_utc = apv.utils.time.convert_settings_localtime_to_UTC(
                SimSettings.sim_date_time, SimSettings.apv_location.tz)
            timeindex = apv.utils.time.get_hour_of_year(sim_dt_utc)
            time = pd.date_range(start=sim_dt_utc, end=sim_dt_utc, freq='1h')
            print(f'energy time: {time} / {timeindex}')
            energy = self.estimate_energy(
                SimSettings=SimSettings,
                APV_SystSettings=self.APV_SystSettings, time=time,
                timeindex=timeindex,
                tmydata=self.tmydata)
            system_energy = energy['p_mp'] \
                * self.APV_SystSettings.sceneDict['nMods'] \
                * self.APV_SystSettings.sceneDict['nRows'] \
                * self.APV_SystSettings.moduleDict['numpanels']
            print(
                f"### TOTAL ENERGY : {energy['p_mp']:.2f} Wh per module ###\n"
                + f'### TOTAL ENERGY: {system_energy/1000:.2f} kWh per system')
        # Generate energy time-series data
        else:
            # gencumsky not used, but cumulated hours energy is calculated
            startdt = apv.utils.time.convert_settings_localtime_to_UTC(
                SimSettings.startdt,
                SimSettings.apv_location.tz)
            enddt = apv.utils.time.convert_settings_localtime_to_UTC(
                SimSettings.enddt,
                SimSettings.apv_location.tz)
            self.csv_file_name = \
                f'eval_energy_{SimSettings.startdt}_{SimSettings.enddt}.csv'
            time = pd.date_range(start=startdt, end=enddt, freq='1h',
                                 closed='right')
            columns = ('Wh/module', 'kWh System')
            print(f'energy time range: {time}')
            self.df_energy_results = pd.DataFrame(columns=columns)
            for t in time:
                timeindex = apv.utils.time.get_hour_of_year(t)
                energy = self.estimate_energy(
                    SimSettings=SimSettings,
                    APV_SystSettings=self.APV_SystSettings,
                    time=t,
                    timeindex=timeindex, tmydata=self.tmydata)
                system_energy = energy['p_mp'] \
                    * self.APV_SystSettings.sceneDict['nMods'] \
                    * self.APV_SystSettings.sceneDict['nRows'] \
                    * self.APV_SystSettings.moduleDict['numpanels'] \
                    / 1000
                self.df_energy_results.loc[t] = (energy['p_mp'], system_energy)

            path = os.path.join(eval_res_path, self.csv_file_name)
            self.df_energy_results.to_csv(path)
            total = self.df_energy_results['kWh System'].sum()
            print(f'### TOTAL ENERGY:{total:.2f} kWh per system')

    def estimate_energy(self, SimSettings, APV_SystSettings, time, timeindex,
                        tmydata):

        # read PV module specs
        input_folder = Path.cwd().parent
        input_folder = os.path.abspath(os.path.join(os.path.dirname(
            pv_modules.__file__), 'Sanyo240_moduleSpecs_guestimate.txt'))
        pv_module: pd.Series = pd.read_csv(input_folder, delimiter='\t').T[0]

        sDict = APV_SystSettings.sceneDict

        # Solar position
        sol_pos = SimSettings.apv_location.get_solarposition(
            time, temperature=tmydata.temp_air.iloc[timeindex])

        # DNI Extraterrestrial from Day_of_year
        dni_extra = pvlib.irradiance.get_extra_radiation(time)

        # Calculate relative airmass
        air_mass = pvlib.atmosphere.get_relative_airmass(
            sol_pos['apparent_zenith'])

        # Calculate pressure
        air_press = pvlib.atmosphere.alt2pres(
            SimSettings.apv_location.altitude)

        # Calculate absolute (corrected) airmass
        air_mass_abs = pvlib.atmosphere.get_absolute_airmass(
            air_mass, air_press)

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

        print('effective Irradiation:\n', effective_irr)

        # Energy generated
        dc = pvlib.pvsystem.sapm(effective_irr, tcell, pv_module)
        total_energy = dc.sum()
        # TODO define inverter
        # ac = pvlib.inverter.sandia(dc['v_mp'], dc['p_mp'], inverter)

        if APV_SystSettings.module_form == 'cell_level_checker_board':
            total_energy = total_energy/2

        return total_energy

    def get_weather_data(self, SimSettings):

        epw = UserPaths.bifacial_radiance_files_folder / Path('EPWs/')
        for file in os.listdir(epw):
            if file.endswith(".epw"):
                epw = os.path.join(UserPaths.bifacial_radiance_files_folder,
                                   'EPWs/', file)
        (self.tmydata, self.metadata) = pvlib.iotools.read_epw(
            epw, coerce_year=2001)
        self.tmydata.index = self.tmydata.index+pd.Timedelta(hours=1)

        if SimSettings.irradiance_data_source == 'ADS_satellite':
            # download data for longest full year time span available
            download_file_path = self.weatherObj.download_insolation_data(
                SimSettings.apv_location, '2005-01-01/2021-01-01', '1hour')
            # make own TMY data
            df_irradiance = self.weatherObj.satellite_irradiance_data_to_TMY(
                download_file_path)
            self.tmydata.ghi = df_irradiance.ghi
            self.tmydata.dhi = df_irradiance.dhi
            self.tmydata.dni = df_irradiance.ghi - df_irradiance.dh

# #
