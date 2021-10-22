''' Uses PVlib to forecast energy yield according to system settings.
'''
# #
from apv.settings.apv_systems import Default
from apv.settings.simulation import Simulation
import sys
from apv.classes.weather_data import WeatherData
from apv.classes.sim_datetime import SimDT
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
class APV_Evaluation:
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
            weatherData=None,
            debug_mode=False
    ):
        self.SimSettings: apv.settings.simulation.Simulation = SimSettings
        self.APV_SystSettings: apv.settings.apv_systems.Default = \
            APV_SystSettings
        if weatherData is None:
            self.weatherData = WeatherData(self.SimSettings)
        else:
            self.weatherData = weatherData
        self.simDT = SimDT(self.SimSettings)
        self.debug_mode = debug_mode
        self.df_energy_results = {}
        self.csv_file_name = str()
        self.tmydata = pd.DataFrame()
        self.irrad_data = pd.DataFrame()

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
                    timeindex=self.simDT.hour_of_tmy_utc,
                    tmydata=self.tmydata,
                    irrad_data=self.irrad_data,
                    sur_azimuth_manual=90)
                energy += self.estimate_energy(
                    SimSettings=SimSettings,
                    APV_SystSettings=self.APV_SystSettings,
                    time=self.simDT.sim_dt_utc_pd,
                    timeindex=self.simDT.hour_of_tmy_utc,
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
                    timeindex=self.simDT.hour_of_tmy_utc,
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

    def estimate_energy(self, SimSettings: Simulation, APV_SystSettings,
                        time, timeindex,
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

    def get_weather_data(self, SimSettings: Simulation):
        """ get EPW to use Temperature and wind speed """
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

            self.irrad_data['ghi'] = self.weatherData.df_irradiance_tmy['GHI']
            self.irrad_data['dhi'] = self.weatherData.df_irradiance_tmy['DHI']
            self.irrad_data['dni'] = self.irrad_data['ghi'] - self.irrad_data['dhi']

    def cumulate_gendaylit_results(
            self,
            file_folder_to_merge, merged_csv_path, SimSettings: Simulation):

        # load all single hour results and append
        df = apv.utils.files_interface.df_from_file_or_folder(
            file_folder_to_merge, append_all_in_folder=True, index_col=0)

        df['xy'] = df['x'].astype(str) + df['y'].astype(str)

        # radiation and PAR
        df_merged = pd.pivot_table(
            df, index=['xy'],
            values=['Wm2', 'PARGround'],
            aggfunc='sum')

        # TODO nicer way?
        df_merged2 = pd.pivot_table(
            df, index=['xy'],
            values=['x', 'y'],
            aggfunc='mean')

        df_merged['x'] = df_merged2['x']
        df_merged['y'] = df_merged2['y']

        df_merged.loc[:, 'Wm2'] *= SimSettings.time_step_in_minutes/60
        df_merged.rename(columns={"Wm2": "Whm2"}, inplace=True)

        # TODO do we have to do this outcommented line: ???
        # df_merged.loc[:, 'PARGround'] *= SimSettings.time_step_in_minutes/60
        df_merged.rename(columns={"PARGround": "PARGround_cum"}, inplace=True)

        # shadow depth cumulative
        df_merged = self.add_shadowdepth(
            df=df_merged, SimSettings=SimSettings, cumulative=True)

        df_merged.to_csv(merged_csv_path)
        print(f'Cumulating hours completed!\n',
              'NOTE: Shadow_depth was recalculated for cumulative data\n')
        return df_merged

    # unit converting:

    @staticmethod
    def add_PAR(df=None):
        """Converts irradiance from [W/m2] to
        Photosynthetic Active Radiation PAR [μmol quanta/ m2.s] [1]

        [1] Čatský, J. (1998): Langhans, R.W., Tibbitts, T.W. (ed.):
        Plant Growth Chamber Handbook. In Photosynt. 35 (2), p. 232.
        DOI: 10.1023/A:1006995714717.

        Args:
            groundscan (DataFrame): [description]
        """
        df['PARGround'] = df['Wm2'] * 4.6

        return df

    def add_shadowdepth(self, df, SimSettings: Simulation, cumulative=False):
        """Shadow Depth is loss of incident solar energy in comparison
        with a non intersected irradiation; if 90% of irradiation available after
        being intersected by objects then the shadow depth is 10% [1][2].

        [1] Miskin, Caleb K.; Li, Yiru; Perna, Allison; Ellis, Ryan G.; Grubbs,
        Elizabeth K.; Bermel, Peter; Agrawal, Rakesh (2019): Sustainable
        co-production of food and solar power to relax land-use constraints. In
        Nat Sustain 2 (10), pp. 972–980. DOI: 10.1038/s41893-019-0388-x.

        [2] Perna, Allison; Grubbs, Elizabeth K.; Agrawal, Rakesh; Bermel, Peter
        (2019): Design Considerations for Agrophotovoltaic Systems: Maintaining PV
        Area with Increased Crop Yield. DOI: 10.1109/PVSC40753.2019.8981324

        Args:
            df (DataFrame): The DataFrame with W.m^-2 values
            SimSettings : self.SimSettings should be given.

            cumulative (bool, optional): used only if cumulative data were used.
            Gencumsky turns this automaticaly to True. Defaults to False.

        Returns:
            [type]: [description]
        """
        simDT = SimDT(SimSettings)
        self.weatherData.set_dhi_dni_ghi_and_sunpos_to_simDT(simDT)

        if SimSettings.sky_gen_mode == 'gendaylit' and not cumulative:
            df['ShadowDepth'] = 100 - ((df['Wm2']/self.weatherData.ghi)*100)

        elif SimSettings.sky_gen_mode == 'gencumsky' or cumulative:
            if SimSettings.use_typical_day_per_month_for_shadow_depth_calculation:
                month = int(SimSettings.sim_date_time.split('-')[0])
                cumulative_GHI = self.weatherData.df_irradiance_typ_day_per_month.loc[
                    (month), 'ghi_Whm-2'].sum()
            else:
                cumulative_GHI = self.weatherData.df_irradiance_tmy.loc[
                    simDT.startdt_utc:simDT.enddt_utc,
                    # +1 is not needed for inclusive end with .loc, only with .iloc
                    'ghi_Wm-2'].sum()

            df['ShadowDepth_cum'] = 100 - ((df['Whm2']/cumulative_GHI)*100)
        return df

    @staticmethod
    def get_label_and_cm_input(cm_unit, cumulative):
        """for the heatmap"""

        if not cumulative:

            if cm_unit == 'radiation':
                unit_parameters = {'z': 'Wm2', 'colormap': 'inferno',
                                   'z_label': 'Irradiance on Ground [W m$^{-2}$]'}

            elif cm_unit == 'shadow_depth':
                unit_parameters = {'z': 'ShadowDepth',  'colormap': 'viridis_r',
                                   'z_label': 'shadow_depth [%]'}

            elif cm_unit == 'PAR':
                unit_parameters = {
                    'z': 'PARGround', 'colormap': 'YlOrBr',
                    'z_label': 'PAR [μmol quanta.m$^{-2}$.s$^{-1}$]'}
            else:
                print('cm_unit has to be radiation, shadow_depth or PAR')

        elif cumulative:

            if cm_unit == 'radiation':
                unit_parameters = {
                    'z': 'Whm2',  'colormap': 'inferno',
                    'z_label': 'Cumulative Irradiation on Ground [Wh m$^{-2}$]'}

            elif cm_unit == 'shadow_depth':
                unit_parameters = {'z': 'ShadowDepth_cum',  'colormap': 'viridis_r',
                                   'z_label': 'Cumulative Shadow Depth [%]'}

            elif cm_unit == 'PAR':  # TODO unit changes also to *h ?
                unit_parameters = {
                    'z': 'PARGround_cum', 'colormap': 'YlOrBr',
                    'z_label': 'Cumulative PAR [μmol quanta.m$^{-2}\cdot s^{-1}$]'}
            else:
                print('cm_unit has to be radiation, shadow_depth or PAR')
        return unit_parameters

# #
