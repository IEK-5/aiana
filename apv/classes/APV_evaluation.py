''' Uses PVlib to forecast energy yield according to system settings.
'''
# #
import os
import sys
import pandas as pd
from pathlib import Path
import pvlib
# import pvfactors
import apv
from apv.settings.apv_systems import Default as APV_System
from apv.settings.simulation import Simulation
from apv.classes.weather_data import WeatherData
from apv.classes.sim_datetime import SimDT
import apv.settings.user_paths as UserPaths
from apv.utils import files_interface as fi


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
            SimSettings: Simulation,
            APV_SystSettings: APV_System,
            weatherData=None,
            debug_mode=False
    ):
        self.SimSettings = SimSettings
        self.APV_SystSettings = APV_SystSettings
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

    def evaluate_APV(self, SimSettings: Simulation):
        """manages estimate_energy according to settings and returns
        final estimates for complete system.


        Args:
            SimSettings ([type]): inherited settings
        """

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
                    self.df_energy_results.loc[t] = (energy['p_mp'],
                                                     system_energy)
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
                    self.df_energy_results.loc[t] = (
                        energy['p_mp'], system_energy)
            # Save csv file containing date and total energy for system
            path = os.path.join(eval_res_path, self.csv_file_name)
            self.df_energy_results.to_csv(path)
            total = self.df_energy_results['kWh System'].sum()
            print(f'### TOTAL ENERGY:{total:.2f} kWh per system')

    def estimate_energy(self, SimSettings: Simulation,
                        APV_SystSettings: APV_System,
                        time, timeindex,
                        tmydata: pd.DataFrame, irrad_data: pd.DataFrame,
                        sur_azimuth_manual=None,
                        ):
        """Use PVlib mathematical model to estimate energy yield. simulation
        steps are as follows:
        1-


        Args:
            SimSettings (Simulation): needed for geographic location location
            APV_SystSettings: inherited APV settings
            pv_module: (pd.Series): as in pvlib
            time ([timestampt UTC]): needed to shift solar position 30m and
                to get extra-terristerial irradiation
            timeindex ([type]): to determine tmydata and irrad_data for hour
            tmydata ([type]): Currently EPW data, used for temperature and wind
                speed, see TODO.
            irrad_data ([type]): ADS data containing GHI,DNI,and DHI
            sur_azimuth_manual ([type], optional): azimuth either read
                automatically from settings or given here for
                EW (1st:90, 2nd:270)

        Returns:
            [return total_energy]: [5 points on IV curve]

        # TODO ADD Bifacial factor
        # TODO Make temperature and wind from CDS
        """

        sDict = self.APV_SystSettings.sceneDict
        surface_azimuth = sur_azimuth_manual or sDict['azimuth']

        # Solar position with 30 minuts shift since time is right-labeled
        sol_pos = SimSettings.apv_location.get_solarposition(
            time-pd.Timedelta('30min'),
            temperature=tmydata['temp_air'].iloc[timeindex-1])
        # SEE NOTE 1 above

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
            dni=irrad_data['dni'].iloc[timeindex],
            ghi=irrad_data['ghi'].iloc[timeindex],
            dhi=irrad_data['dhi'].iloc[timeindex], dni_extra=dni_extra,
            model='isotropic')

        print(total_irr)

        # PV cell temperature TODO make glass-glass only if bifacial
        temperature_model_parameters = pvlib.temperature\
            .TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
        tcell = pvlib.temperature.sapm_cell(
            total_irr['poa_global'],
            temp_air=tmydata['temp_air'].iloc[timeindex-1],  # SEE NOTE 1 above
            wind_speed=tmydata['wind_speed'].iloc[timeindex-1],  # See NOTE 1
            **temperature_model_parameters)

        # Effective Irradiation on array
        effective_irr = pvlib.pvsystem.sapm_effective_irradiance(
            total_irr['poa_direct'], total_irr['poa_diffuse'],
            air_mass_abs, aoi, self.APV_SystSettings.moduleSpecs)

        print('effective Irradiation:\n', effective_irr)

        # Energy generated
        dc = pvlib.pvsystem.sapm(
            effective_irr, tcell, self.APV_SystSettings.moduleSpecs)
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
        self.irrad_data: pd.DataFrame = pd.read_csv(
            epw_csv, sep=' ')
        self.irrad_data.columns = ['ghi', 'dhi']
        self.irrad_data['dni'] = self.irrad_data['ghi']-self.irrad_data['dhi']
        print(self.irrad_data.head(10))
        # Overwrite irradiation data only with ADS data
        if SimSettings.irradiance_data_source == 'ADS_satellite':

            self.irrad_data['ghi'] = self.weatherData.df_irradiance_tmy['GHI']
            self.irrad_data['dhi'] = self.weatherData.df_irradiance_tmy['DHI']
            self.irrad_data['dni'] = self.irrad_data['ghi'] \
                - self.irrad_data['dhi']

    def cumulate_gendaylit_results(
            self,
            file_folder_to_merge, cum_csv_path, SimSettings: Simulation):

        # load all single results and append
        df = apv.utils.files_interface.df_from_file_or_folder(
            file_folder_to_merge, append_all_in_folder=True, index_col=0)

        df['xy'] = df['x'].astype(str) + df['y'].astype(str)

        # radiation and PAR
        df_merged = pd.pivot_table(
            df, index=['xy'],
            values=['Wm2', 'PARGround'],
            aggfunc='sum')

        # TODO nicer way?  currently it results in two x and two y columns!
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
        # Add Daily Light integral
        df_merged['DLI'] = df_merged['Whm2']*4.6*0.45*3600/1000000
        # shadow depth cumulative
        df_merged = self.add_shadowdepth(
            df=df_merged, SimSettings=SimSettings, cumulative=True)

        df_merged.to_csv(cum_csv_path)
        print(f'Cumulating completed!\n',
              'NOTE: Shadow_depth was recalculated for cumulative data\n')
        return df_merged

    @staticmethod
    def monthly_avg_std(
        data: pd.DataFrame, column, group_by
    ):
        """From appended data, creates a dataframe of average and std of
        each month

        Args:
            data (DataFrame): complete appended data with Month column
            column (str): which column to find avg and std to
            group_by (str): group by 'Month'

        Returns:
            [DataFrame]: [df with avg and std per month]
        """
        means = data[column].groupby(data[group_by]).mean()
        stds = data[column].groupby(data[group_by]).std()
        df = pd.DataFrame(means)
        df['std'] = stds
        print(df)

        return df

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
        with a non intersected irradiation; if 90% of irradiation available
        after being intersected by objects then the shadow depth is 10% [1][2].

        if clouds are considered as objects, one should compare to clearSky ghi

        [1] Miskin, Caleb K.; Li, Yiru; Perna, Allison; Ellis, Ryan G.; Grubbs,
        Elizabeth K.; Bermel, Peter; Agrawal, Rakesh (2019): Sustainable
        co-production of food and solar power to relax land-use constraints. In
        Nat Sustain 2 (10), pp. 972–980. DOI: 10.1038/s41893-019-0388-x.

        [2] Perna, Allison; Grubbs, Elizabeth K.; Agrawal, Rakesh; Bermel,
        Peter (2019): Design Considerations for Agrophotovoltaic Systems:
        Maintaining PV Area with Increased Crop Yield.
        DOI: 10.1109/PVSC40753.2019.8981324

        Args:
            df (DataFrame): The DataFrame with W.m^-2 values
            SimSettings : self.SimSettings should be given.

            cumulative (bool, optional): used only if cumulative data were
            used. Gencumsky turns this automaticaly to True. Defaults to False.

        Returns:
            [type]: [description]
        """
        simDT = SimDT(SimSettings)
        self.weatherData.set_dhi_dni_ghi_and_sunpos_to_simDT(simDT)

        if SimSettings.sky_gen_mode == 'gendaylit' and not cumulative:
            # instant shadow depth
            df['ShadowDepth'] = 100 - (
                (df['Wm2']/self.weatherData.ghi_clearsky)*100)

        elif SimSettings.sky_gen_mode == 'gencumsky' or cumulative:
            # cumulated shadow depth
            if SimSettings.use_typDay_perMonth_for_shadowDepthCalculation:
                month = int(SimSettings.sim_date_time.split('-')[0])
                cumulative_GHI = \
                    self.weatherData.df_irradiance_typ_day_per_month.loc[
                        (month), 'ghi_clearSky_Whm-2'].sum()
            else:
                cumulative_GHI = self.weatherData.df_irr.loc[
                    simDT.startdt_utc:simDT.enddt_utc,
                    # +1 is not needed for inclusive end with .loc,
                    # only with .iloc
                    'ghi_clearSky_Whm-2'].sum()

            df['ShadowDepth_cum'] = 100 - ((df['Whm2']/cumulative_GHI)*100)
            print(SimSettings.TMY_irradiance_aggfunc, 'cum clearSky ghi: ',
                  cumulative_GHI)
        return df

    @staticmethod
    def get_label_and_cm_input(cm_unit, cumulative,
                               df_col_limits: pd.DataFrame = None):
        """for the heatmap"""

        # #################################### #
        if cm_unit == 'radiation':
            input_dict = {'colormap': 'inferno'}
            if cumulative:
                dict_up = {'z': 'Whm2', 'z_label':
                           'Cumulative Irradiation on Ground [Wh m$^{-2}$]'}
            else:
                dict_up = {'z': 'Wm2', 'z_label':
                           'Irradiance on Ground [W m$^{-2}$]'}
        # #################################### #
        elif cm_unit == 'shadow_depth':
            input_dict = {'colormap': 'viridis_r'}
            if cumulative:
                dict_up = {'z': 'ShadowDepth_cum', 'z_label':
                           'Cumulative Shadow Depth [%]'}
            else:
                dict_up = {'z': 'ShadowDepth', 'z_label': 'Shadow Depth [%]'}
        # #################################### #
        elif cm_unit == 'PAR':  # TODO unit changes also to *h ?
            input_dict = {'colormap': 'YlOrBr_r'}
            if cumulative:
                dict_up = {'z': 'PARGround_cum', 'z_label': 'Cumulative PAR'
                           + r' [μmol quanta.m$^{-2}\cdot s^{-1}$]'}
            else:
                dict_up = {'z': 'PARGround', 'z_label':
                           'PAR [μmol quanta.m$^{-2}$.s$^{-1}$]'}
        # #################################### #
        elif cm_unit == 'DLI':
            input_dict = {'colormap': 'YlOrBr_r'}
            if cumulative:
                dict_up = {'z': 'DLI', 'z_label':
                           r'DLI [mol quanta.m$^{-2}\cdot day^{-1}$]'}
            else:
                sys.exit('cm_unit = DLI is only for cumulative')
        else:
            sys.exit('cm_unit has to be radiation, shadow_depth, PAR or DLI')

        input_dict.update(dict_up)

        if df_col_limits is None:
            input_dict['vmin'] = None
            input_dict['vmax'] = None
        else:
            input_dict['vmin'] = df_col_limits.loc['min', input_dict['z']]
            input_dict['vmax'] = df_col_limits.loc['max', input_dict['z']]

        return input_dict

# #
