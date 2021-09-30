''' Uses PVlib to forecast energy yield according to system settings.
'''
# #
from apv.settings.apv_systems import Default
from apv.settings.simulation import Simulation
import sys
from apv.utils.weather_data import WeatherData
from apv.utils.time import SimDT
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
    # NOTE 1: The temperature and wind speed are taken from EPW data that has
    # time index in local time. A -1 was added as a quick fix for the case in
    # Germany. This should be amended by either change EPW time index to UTC or
    # use Temperature and wind speed from other data source like CDS.

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
        self.simDT = SimDT(self.SimSettings)
        self.debug_mode = debug_mode
        self.df_energy_results = {}
        self.csv_file_name = str()
        self.tmydata = pd.DataFrame()

    def evaluate_APV(self, SimSettings):

        # Adjust settings
        self.APV_SystSettings = apv.utils.settings_adjuster.adjust_settings(
            self.APV_SystSettings)
        # read EPW data from bifacial radiance files
        self.get_weather_data(SimSettings)
        # View energy generated on specific date-time
        if SimSettings.sky_gen_mode == 'gendaylit':
            if self.APV_SystSettings.module_form == 'EW_fixed' or \
               self.APV_SystSettings.module_form == 'cell_level_EW_fixed':
                energy = self.estimate_energy(
                    SimSettings=SimSettings,
                    APV_SystSettings=self.APV_SystSettings,
                    time=self.simDT.sim_dt_utc_pd,
                    timeindex=self.simDT.hour_of_tmy,
                    tmydata=self.tmydata,
                    irrad_data=self.irrad_data,
                    sur_azimuth_manual=90)
                energy += self.estimate_energy(
                    SimSettings=SimSettings,
                    APV_SystSettings=self.APV_SystSettings,
                    time=self.simDT.sim_dt_utc_pd,
                    timeindex=self.simDT.hour_of_tmy,
                    tmydata=self.tmydata,
                    irrad_data=self.irrad_data,
                    sur_azimuth_manual=270)
                system_energy = energy['p_mp'] \
                    * self.APV_SystSettings.sceneDict['nMods'] \
                    * self.APV_SystSettings.sceneDict['nRows']
            else:
                energy = self.estimate_energy(
                    SimSettings=SimSettings,
                    APV_SystSettings=self.APV_SystSettings,
                    time=self.simDT.sim_dt_utc_pd,
                    timeindex=self.simDT.hour_of_tmy,
                    tmydata=self.tmydata,
                    irrad_data=self.irrad_data)
                system_energy = energy['p_mp'] \
                    * self.APV_SystSettings.sceneDict['nMods'] \
                    * self.APV_SystSettings.sceneDict['nRows'] \
                    * self.APV_SystSettings.moduleDict['numpanels']
            print(
                f"### TOTAL ENERGY : {energy['p_mp']:.2f} Wh per module ###\n"
                + f'### TOTAL ENERGY: {system_energy/1000:.2f} kWh per system')
        # Generate energy time-series data
        else:
            # Create results folder
            eval_res_path = UserPaths.results_folder / Path('Evaluation/')
            fi.make_dirs_if_not_there(eval_res_path)
            self.csv_file_name = f'eval_energy_{SimSettings.startdt} \
                 _{SimSettings.enddt}_{self.APV_SystSettings.module_form}.csv'
            columns = ('Wh/module', 'kWh System')
            # print(f'energy times range: {self.simDT.times}')
            self.df_energy_results = pd.DataFrame(columns=columns)
            for t in self.simDT.times:
                timeindex = self.simDT.get_hour_of_tmy(t)
                if self.APV_SystSettings.module_form == 'cell_level_EW_fixed'\
                        or self.APV_SystSettings.module_form == 'EW_fixed':
                    energy = self.estimate_energy(
                        SimSettings=SimSettings,
                        APV_SystSettings=self.APV_SystSettings,
                        time=t, timeindex=timeindex, tmydata=self.tmydata,
                        irrad_data=self.irrad_data, sur_azimuth_manual=90)
                    energy += self.estimate_energy(
                        SimSettings=SimSettings,
                        APV_SystSettings=self.APV_SystSettings,
                        time=t, timeindex=timeindex, tmydata=self.tmydata,
                        irrad_data=self.irrad_data, sur_azimuth_manual=270)
                    system_energy = energy['p_mp'] \
                        * self.APV_SystSettings.sceneDict['nMods'] \
                        * self.APV_SystSettings.sceneDict['nRows'] \
                        / 1000
            else:
                energy = self.estimate_energy(
                    SimSettings=SimSettings,
                    APV_SystSettings=self.APV_SystSettings,
                    time=t,
                    timeindex=timeindex, tmydata=self.tmydata,
                    irrad_data=self.irrad_data)
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
                        tmydata, irrad_data, sur_azimuth_manual=None):

        sDict = self.APV_SystSettings.sceneDict
        # read PV module specs
        input_folder = Path.cwd().parent
        input_folder = os.path.abspath(os.path.join(os.path.dirname(
            pv_modules.__file__), 'Sanyo240_moduleSpecs_guestimate.txt'))
        pv_module: pd.Series = pd.read_csv(input_folder, delimiter='\t').T[0]
        surface_azimuth = sur_azimuth_manual or sDict['azimuth']

        # Solar position with 30 minuts shift since time is right-labeled
        sol_pos = SimSettings.apv_location.get_solarposition(
            time-pd.Timedelta('30min'),
            temperature=tmydata.temp_air.iloc[timeindex-1])  # SEE NOTE 1 above

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
            surface_tilt=sDict['tilt'], surface_azimuth=surface_azimuth,
            solar_zenith=sol_pos['apparent_zenith'],
            solar_azimuth=sol_pos['azimuth']
        )
        # Plane of Array (POA) Irradiation
        total_irr = pvlib.irradiance.get_total_irradiance(
            surface_tilt=sDict['tilt'],
            surface_azimuth=surface_azimuth,
            solar_zenith=sol_pos['apparent_zenith'],
            solar_azimuth=sol_pos['azimuth'],
            dni=irrad_data.dni.iloc[timeindex],
            ghi=irrad_data.ghi.iloc[timeindex],
            dhi=irrad_data.dhi.iloc[timeindex], dni_extra=dni_extra,
            model='isotropic')

        print(total_irr)

        # PV cell temperature TODO make glass-glass only if bifacial
        temperature_model_parameters = pvlib.temperature\
            .TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
        tcell = pvlib.temperature.sapm_cell(
            total_irr['poa_global'],
            temp_air=tmydata.temp_air.iloc[timeindex-1],  # SEE NOTE 1 above
            wind_speed=tmydata.wind_speed.iloc[timeindex-1],  # See NOTE 1
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
        # get EPW to use Temperature and wind speed
        epw = UserPaths.bifacial_radiance_files_folder / Path('EPWs/')
        for file in os.listdir(epw):
            if file.endswith(".epw"):
                epw = os.path.join(UserPaths.bifacial_radiance_files_folder,
                                   'EPWs/', file)
        (self.tmydata, self.metadata) = pvlib.iotools.read_epw(
            epw, coerce_year=2001)
        # TODO reset to UTC
        # NOTE: In PVLib > 0.6.1 the new epw.read_epw() function reads in time
        # with a default - 1 hour offset.  This is not reflected in our
        # existing workflow, and must be investigated further.
        self.tmydata.index = self.tmydata.index+pd.Timedelta(hours=1)

        # get EPW.csv to use GHI and DHI
        epw_csv = UserPaths.bifacial_radiance_files_folder / Path('EPWs/')
        for file in os.listdir(epw_csv):
            if file.endswith(".csv"):
                epw_csv = os.path.join(
                    UserPaths.bifacial_radiance_files_folder, 'EPWs/', file)
        self.irrad_data = pd.read_csv(
            epw_csv, sep=' ')
        self.irrad_data.columns = ['ghi', 'dhi']
        self.irrad_data['dni'] = self.irrad_data.ghi - self.irrad_data.dhi
        print(self.irrad_data.head(10))
        # Overwrite irradiation data only with ADS data
        if SimSettings.irradiance_data_source == 'ADS_satellite':
            # download data for longest full year time span available
            download_file_path = self.weatherObj.download_insolation_data(
                self.SimSettings.apv_location,
                '2005-01-01/2021-01-01', '1hour')
            # make/read own TMY data
            ADS_irradiance = self.weatherObj.satellite_insolation_data_to_TMY(
                download_file_path)
            self.irrad_data['ghi'] = ADS_irradiance.ghi
            self.irrad_data['dhi'] = ADS_irradiance.dhi
            self.irrad_data['dni'] = ADS_irradiance.ghi - ADS_irradiance.dhi

# #
