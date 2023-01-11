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
from pathlib import Path
import pandas as pd
from aiana.utils import files_interface as fi
from aiana.classes.weather_data import WeatherData
from aiana.classes.util_classes.sim_datetime import SimDT
from aiana.classes.util_classes.settings_handler import Settings


class Evaluator:

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

    def evaluate_csv(self):
        """renames columns and adds result columns to csv
        """

        df: pd.DataFrame = fi.df_from_file_or_folder(
            self.settings._paths.inst_csv_file_path,
            print_reading_messages=False)
        df = df.reset_index()

        df['time_local'] = self.settings._dt.sim_dt_naiv
        df['time_utc'] = self.settings._dt.sim_dt_utc

        # if 'ground' in str(self.settings.paths.csv_file_path): # TODO needed?
        df.rename(columns={'Wm2Front': 'Wm2'}, inplace=True)

        df = self._add_PAR(df=df)
        df = self._add_shadowdepth(df=df, cumulative=False)

        df.to_csv(self.settings._paths.inst_csv_file_path)

        print(f'Evaluated {self.settings._paths.inst_csv_file_path}')
        self.df_ground_results = df

    @staticmethod
    def _add_PAR(df: pd.DataFrame) -> pd.DataFrame:
        """Converts irradiance from [W/m^2] to
        Photosynthetic Active Radiation (PAR) [μmol quanta / (m^2*s)] [1]

        [1] Čatský, J. (1998): Langhans, R.W., Tibbitts, T.W. (ed.):
        Plant Growth Chamber Handbook. In Photosynt. 35 (2), p. 232.
        DOI: 10.1023/A:1006995714717. (Chapt1., p.3, table2)

        Args:
            df (pd.DataFrame): with a 'Wm2' column
        """
        df['PARGround'] = df['Wm2'] * 4.57
        return df

    def _add_shadowdepth(
            self, df: pd.DataFrame, cumulative=False) -> pd.DataFrame:
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
            df (DataFrame): The DataFrame with irradiance data in W/m² if not
            cumulative or with irradiation data in Wh/m² if cumulative.

            cumulative (bool, optional): to switch between instantaneous and
            cumulative calculation. Defaults to False.

            Gencumsky turns this automaticaly to True.
            #TODO gencumsky is not in use atm !

        Returns:
            [type]: [description]
        """

        if self.settings.sim.for_shadowDepths_compare_GGI_to == 'clearsky_GHI':
            ghi_ref = self.weatherData.ghi_clearsky
            cum_ghi_ref = self.weatherData.dailyCumulated_ghi_clearsky
        elif self.settings.sim.for_shadowDepths_compare_GGI_to \
                == 'GHI_as_TMY_aggfunc':
            ghi_ref = self.weatherData.ghi
            cum_ghi_ref = self.weatherData.dailyCumulated_ghi
        else:
            raise Exception('settings.sim.for_shadowDepths_compare_GGI_to has to '
                            'be set to "clearsky_GHI" or "GHI_as_TMY_aggfunc".')

        # instantaneous shadow depth
        if self.settings.sim.sky_gen_mode == 'gendaylit' and not cumulative:
            df['ShadowDepth'] = 100 * (1 - df['Wm2']/ghi_ref)

        # cumulated shadow depth:
        elif self.settings.sim.sky_gen_mode == 'gencumsky' or cumulative:
            df['ShadowDepth_cum'] = 100 * (1 - df['Whm2']/cum_ghi_ref)
            print(self.settings.sim.irradiance_aggfunc,
                  'cum clearSky ghi: ', cum_ghi_ref)

        return df

    @staticmethod
    def _add_DLI(df_merged: pd.DataFrame) -> pd.DataFrame:
        """Add Daily Light Integral (DLI [mol/m²])

        Args:
            df (pd.DataFrame): daily cumulated irradiation with a Whm2 column
        """

        df_merged['DLI'] = df_merged['Whm2']*0.0074034
        """0.0074034 = 4.57  [ref1]  * 0.45 [ref2] *3600/1000000
        # mol quanta / m² = W*h/m² * µmol quanta/(s*m²) * (3600s/h) / (µ*1E6)
        [ref1] Catsky1998 Plant growth chamber handbook, Chapt1., p.3, table2
        [ref2] Faust2018, HORTSCIENCE 53(9):1250–1257.
        https://doi.org/10.21273/HORTSCI13144-18"""

        return df_merged

    def cumulate_results(self,
                         file_folder_to_merge: Path = None,
                         cum_csv_path: Path = None,
                         add_DLI=False) -> pd.DataFrame:
        """cumulates the gendaylit results

        Args:
            file_folder_to_merge (Path): source/input FOLDER path
            all single gendaylit simulation result files in this folder path
            will be merged. Defaults to self.settings.paths.csv_parent_folder,
            built by settings_handler from
            results_subfolder/'inst_data'
            with results_subfolder defined in settings/user_paths.py.

            Sub folders within file_folder_to_merge are ignored.

            cum_csv_file_path (Path): destination/output FILE path,
            defaults to file_folder_to_merge.parent/"cumulated.csv"
            with SimSettings.results_subfolder defined in user_paths

            add_DLI (bool, optional): Whether to add a Daily Light Integral
            column. Should only be set True if the cumulated timespan is
            a full day! Defaults to False.

        Returns:
            _type_: _description_
        """

        if file_folder_to_merge is None:
            file_folder_to_merge: Path = self.settings._paths.inst_csv_parent_folder
        if cum_csv_path is None:
            cum_csv_path: Path = self.settings._paths.cum_csv_file_path

        # load all single results and append
        df = fi.df_from_file_or_folder(
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
        print(f'Cumulating completed.\n')
        return df_merged
