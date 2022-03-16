import pandas as pd
from apv.classes.weather_data import WeatherData
from apv.classes.util_classes.sim_datetime import SimDT
from apv.classes.util_classes.settings_grouper import Settings
from apv.utils import files_interface as fi


class Evaluator:

    # TODO Wm2 rename to W/m^2 possible?
    # TODO header now sometimes = quantity name, sometimes = unit... unify!
    # TODO ADD Bifacial factor

    def __init__(
            self,
            settings: Settings,
            weatherData: WeatherData,
            debug_mode=False
    ):
        self.settings = settings
        self.weatherData = weatherData
        self.debug_mode = debug_mode
        self.simDT = SimDT(self.settings.sim)

    def add_time_stamps_PAR_shadowDepth_to_csv_file(self):

        df: pd.DataFrame = fi.df_from_file_or_folder(
            self.settings.paths.csv_file_path,
            print_reading_messages=False)
        df = df.reset_index()

        df['time_local'] = self.simDT.sim_dt_local
        df['time_utc'] = self.simDT.sim_dt_utc_pd

        if 'ground' in str(self.settings.paths.csv_file_path):
            df.rename(columns={'Wm2Front': 'Wm2'}, inplace=True)

        df = self._add_PAR(df=df)
        df = self._add_shadowdepth(df=df, cumulative=False)

        df.to_csv(self.settings.paths.csv_file_path)

        print(f'Evaluated {self.settings.paths.csv_file_path}\n')
        self.df_ground_results = df

    @staticmethod
    def _add_PAR(df: pd.DataFrame) -> pd.DataFrame:
        """Converts irradiance from [W/m2] to
        Photosynthetic Active Radiation (PAR) [μmol quanta/ m2.s] [1]

        [1] Čatský, J. (1998): Langhans, R.W., Tibbitts, T.W. (ed.):
        Plant Growth Chamber Handbook. In Photosynt. 35 (2), p. 232.
        DOI: 10.1023/A:1006995714717. (Chapt1., p.3, table2)

        Args:
            df (pd.DataFrame): with a 'Wm2' column
        """
        df['PARGround'] = df['Wm2'] * 4.57
        return df

    @staticmethod
    def _add_DLI(df_merged: pd.DataFrame) -> pd.DataFrame:
        """Add Daily Light Integral (DLI)

        Args:
            df (pd.DataFrame): daily cumulated irradiation with a Wh/m^2 column
        """

        df_merged['DLI'] = df_merged['Whm2']*0.0074034
        """0.0074034 = 4.57  [ref1]  * 0.45 [ref2] *3600/1000000
        # mol quanta / m² = W*h/m² * µmol quanta/(sec*m²) * (3600s/h) / (µ*1E6)
        [ref1] Catsky1998 Plant growth chamber handbook, Chapt1., p.3, table2
        [ref2] Faust2018, HORTSCIENCE 53(9):1250–1257.
        https://doi.org/10.21273/HORTSCI13144-18"""

        return df_merged

    def _add_shadowdepth(self, df, cumulative=False):
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
            df (DataFrame): The DataFrame with irradiance (W/m² not cumulative)
            or irradiation (Wh/m², cumulative) data
            SimSettings : self.settings.sim should be given.

            cumulative (bool, optional): used only if cumulative data were
            used. Gencumsky turns this automaticaly to True. Defaults to False.

        Returns:
            [type]: [description]

        TODO cumulative GHI now calculated already in weatherData as
        as it is also needed for ghi filter. Here start and end for cumulative
        are calculated by ghi filter setted start and end time stamps
        in weatherData this cannot be known, so complete day will be used...
        what is better?

        and also: should shadowdepth be compared to clearsky or not?
        probably make a setting for it and offer both

        """
        # refresh time to allow for looping cumulative evaluation from outside
        simDT = SimDT(self.settings.sim)
        self.weatherData.set_dhi_dni_ghi_and_sunpos_to_simDT(simDT)

        if self.settings.sim.sky_gen_mode == 'gendaylit' and not cumulative:
            # instant shadow depth
            df['ShadowDepth'] = 100 - (
                (df['Wm2']/self.weatherData.ghi_clearsky)*100)

        elif self.settings.sim.sky_gen_mode == 'gencumsky' or cumulative:
            # cumulated shadow depth
            if self.settings.sim.use_typDay_perMonth_for_irradianceCalculation:
                month = int(self.settings.sim.sim_date_time.split('-')[0])
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
            print(self.settings.sim.TMY_irradiance_aggfunc,
                  'cum clearSky ghi: ',
                  cumulative_GHI)
        return df

    def cumulate_gendaylit_results(
            self, file_folder_to_merge, cum_csv_path, add_DLI=False):
        """add_DLI should only be set True, if cumulated timespan is a day"""

        # load all single results and append
        df = fi.df_from_file_or_folder(
            file_folder_to_merge, append_all_in_folder=True, index_col=0)

        df['xy'] = df['x'].astype(str) + df['y'].astype(str)

        # radiation and PAR
        df_merged = pd.pivot_table(
            df, index=['xy'],
            values=['Wm2', 'PARGround'],
            aggfunc='sum')

        # TODO M| nicer way?  currently it results in two x and two y columns!
        df_merged2 = pd.pivot_table(
            df, index=['xy'],
            values=['x', 'y'],
            aggfunc='mean')

        df_merged['x'] = df_merged2['x']
        df_merged['y'] = df_merged2['y']

        # convert power to energy:
        for q in ['Wm2', 'PARGround']:
            df_merged.loc[:, q] *= self.settings.sim.time_step_in_minutes/60
        df_merged.rename(
            columns={"Wm2": "Whm2", "PARGround": "PARGround_cum"}, inplace=True
        )

        # shadow depth cumulative
        df_merged: pd.DataFrame = self._add_shadowdepth(
            df_merged, cumulative=True)
        if add_DLI:
            df_merged: pd.DataFrame = self._add_DLI(df_merged)

        df_merged.to_csv(cum_csv_path)
        print(f'Cumulating completed!\n',
              'NOTE: Shadow_depth was recalculated for cumulative data\n')
        return df_merged
