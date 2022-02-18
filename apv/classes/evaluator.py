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
from apv.classes.util_classes.sim_datetime import SimDT
import apv.settings.user_paths as UserPaths
from apv.classes.util_classes.settings_grouper import Settings
from apv.utils import files_interface as fi


# #
class Evaluator:
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
            settings: Settings,
            weatherData: WeatherData,
            debug_mode=False
    ):
        self.settings = settings
        self.weatherData = weatherData
        self.debug_mode = debug_mode
        self.simDT = SimDT(self.settings.sim)

        #self.df_energy_results = {}

    def add_time_stamps_PAR_shadowDepth_to_csv_file(self):
        """merge results to create one complete ground DataFrame
        """

        df: pd.DataFrame = fi.df_from_file_or_folder(
            self.settings.paths.csv_file_path,
            print_reading_messages=False)
        df = df.reset_index()

        df['time_local'] = self.simDT.sim_dt_local
        df['time_utc'] = self.simDT.sim_dt_utc_pd

        df = self._add_PAR(df=df)
        df = self._add_shadowdepth(df=df, cumulative=False)

        df.to_csv(self.settings.paths.csv_file_path)

        print(f'merged file saved in {self.settings.paths.csv_file_path}\n')
        self.df_ground_results = df

    @staticmethod
    def _add_PAR(df=None):
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
            df (DataFrame): The DataFrame with W.m^-2 values
            SimSettings : self.settings.sim should be given.

            cumulative (bool, optional): used only if cumulative data were
            used. Gencumsky turns this automaticaly to True. Defaults to False.

        Returns:
            [type]: [description]
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
            if self.settings.sim.use_typDay_perMonth_for_shadowDepthCalculation:
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
            print(self.settings.sim.TMY_irradiance_aggfunc, 'cum clearSky ghi: ',
                  cumulative_GHI)
        return df


# #
