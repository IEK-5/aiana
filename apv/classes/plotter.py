
import copy
from pathlib import Path
import sys
from typing import Literal
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
import pandas as pd
from apv.classes.rad_txt_related.geometries_handler import GeometriesHandler
from apv.classes.util_classes.settings_handler import Settings
from apv.utils import plotting_utils as plotting, study_utils
from apv.utils import files_interface as fi
import seaborn as sns


class Plotter:

    def __init__(
            self,
            settings: Settings,
            ghObj: GeometriesHandler,
            # debug_mode=False
    ):
        self.settings = settings
        self.ghObj = ghObj

    def ground_heatmap(
        self,
        df: pd.DataFrame = None,
        cm_quantity: str = None,
        cumulative: bool = False,
        destination_file_path: Path = None,
        plot_dpi: int = None,
        north_arrow_xy_posi: tuple = None,
        plot_title: str = None,
        col_bar_min: float = None,
        col_bar_max: float = None,
        df_col_limits: pd.DataFrame = None,
        ticklabel_format='{:.1f}'
    ):
        """plots the ground insolation as a heat map and saves it into
            the results/plots folder.

        Args:
            df (pd.DataFrame): if None, a df is created
            from the csv file name stored in an instance of this class.
            Defaults to None.

            cm_quantity: Literal['radiation', 'PAR', 'shadow_depth', 'DLI']
            if None, value of sim_settings.cm_quantity is used.

            df_col_limits (pd.DataFrame): with same columns as in df with a min
            and max row (as e.g. returned by df_concatenated.agg([min, max]))
            to be used as color bar limits.
            Defaults to None.
            col_bar_min or max: overwrites df_col_limits

            if an ax is passed, the plot is placed into the ax.
        """

        if df is None:
            if cumulative:
                fp = self.settings._paths.cum_csv_file_path
            else:
                fp = self.settings._paths.inst_csv_file_path
            if fp.exists():
                df = fi.df_from_file_or_folder(str(fp))
            else:
                raise Exception(f"Can't plot, file path {fp} not found.")
        if cm_quantity is None:
            cm_quantity = self.settings.sim.cm_quantity

        if plot_dpi is None:
            plot_dpi = self.settings.sim.plot_dpi

        if north_arrow_xy_posi is None:
            north_arrow_xy_posi = self.settings.sim.north_arrow_xy_posi

        if plot_title is None:
            plot_title = self.return_plot_title(cumulative)

        if df_col_limits is None:
            df_col_limits = df.agg([min, max])
        if col_bar_min is not None:
            df_col_limits.loc['min', cm_quantity] = col_bar_min
        if col_bar_max is not None:
            df_col_limits.loc['max', cm_quantity] = col_bar_max

        label_and_cm_input: dict = self.get_label_and_cm_input(
            cm_unit=cm_quantity, cumulative=cumulative,
            df_col_limits=df_col_limits)

        ticklabels_skip_count_number = int(
            round(self.ghObj.scan_length_x, 0)
            / (4*self.settings.sim.spatial_resolution))
        # the finer the resolution (lower), the more ticks labels
        # need to be skipped (higher) thats why count = 1/res

        if ticklabels_skip_count_number < 2:
            ticklabels_skip_count_number = "auto"

        # round to 10th of mm to avoid a bug that same coordinates are not
        # treated as one due to floating precicion behaviour:
        df = df.round({'x': 4, 'y': 4})
        fig, ax = plt.subplots(1, 1)

        ax = plotting.plot_heatmap(
            df=df, x='x', y='y', c=label_and_cm_input['z'],
            cm=label_and_cm_input['colormap'],
            x_label='x [m]', y_label='y [m]',
            z_label=label_and_cm_input['z_label'],
            tick_label_format=ticklabel_format,
            plot_title=plot_title,
            ticklabels_skip_count_number=ticklabels_skip_count_number,
            vmin=label_and_cm_input['vmin'],
            vmax=label_and_cm_input['vmax'],
            ax_blanc=ax
        )

        ax = plotting.add_north_arrow(
            ax, xy=north_arrow_xy_posi,
            panel_azimuth=self.settings.apv.sceneDict['azimuth']
        )

        if destination_file_path is None:
            if cumulative:
                destination_file_path = self.settings._paths.cum_plot_file_path
            else:
                destination_file_path = self.settings._paths.inst_plot_file_path

        fi.save_fig(fig, destination_file_path, dpi=plot_dpi)

    def box_plot_month_comparing(self, df: pd.DataFrame, ax_blanc: Axes = None,
                                 y='DLI', ref_y: pd.DataFrame = None):
        """for cumulative data
        y type: literal as in settings.sim.cm_quantity
        ['radiation', 'PAR', 'shadow_depth', 'DLI']
        #TODO heatmap z becomes here y, rename?
        """
        sns.set_theme(style="darkgrid")

        label_and_cm_input: dict = self.get_label_and_cm_input(
            cm_unit=y, cumulative=True)

        if ax_blanc is not None:
            ax = ax_blanc
        else:
            fig, ax = plt.subplots()

        ax = sns.boxplot(x="Month", y=label_and_cm_input['z'],
                         data=df, palette="autumn", ax=ax)

        if y == 'DLI' and ref_y is not None:  # TODO add GHI, unify col label
            ax = sns.stripplot(x='Month', y='refDLI', dodge=False,
                               marker='*', size=10,
                               data=ref_y, color='black', ax=ax)

        # ax.set_title(df.name)
        ax.set_ylabel(label_and_cm_input['z_label'])
        ax.grid(True)

        return ax

    def return_weather_description(self) -> (
            Literal['max cloudy', 'mean cloudy', 'clear sky'] | None):
        aggfunc = self.settings.sim.TMY_irradiance_aggfunc
        if aggfunc == 'min':
            return 'max cloudy'
        if aggfunc == 'mean':
            return 'mean cloudy'
        if aggfunc == 'max':
            return 'clear sky'  # TODO take clear_sky values then?
        else:
            raise ValueError(
                f'settings.sim.TMY_irradiance_aggfunc has to be '
                f'"min", "mean", or "max" but was set to "{aggfunc}".')

    def return_plot_title(self, cumulative: bool, title_comps=None) -> str:
        if title_comps is None:
            title_comps = self.settings.sim.plot_title_components
        title = ''

        if 'sub_study_name' in title_comps:
            title += f'{self.settings.sim.sub_study_name}\n'
        if 'weather' in title_comps:
            title += f'Weather: {self.return_weather_description()}\n'
        if 'agg_func' in title_comps:  # redundant to weather
            title += (f'TMY aggregation function: '
                      f'{self.settings.sim.TMY_irradiance_aggfunc}\n')
        if 'resolution' in title_comps:
            title += f'Resolution: {self.settings.sim.spatial_resolution} m\n'
        if 'position' in title_comps:
            title += f'Scanned Position: {self.settings.sim.scan_position}\n'
        if 'module_form' in title_comps:
            title += f'Module Form: {self.settings.apv.module_form}'
        if 'datetime' in title_comps:
            title += f'\nDate: {self.settings._dt.sim_dt_str.split(" ")[0]}'
            if cumulative:
                end_time: str = self.settings._dt.end_dt_str.split(" ")[1]
                start_time: str = self.settings._dt.start_dt_str.split(" ")[1]
                title += f'\nLocal time span: {start_time} to {end_time}'
            else:
                sim_time: str = self.settings._dt.sim_dt_str.split(" ")[1]
                title += f'\nIrradiance mean from: '\
                         + self.settings._dt.irradiance_mean_timeSpan_start_str\
                         + f' to {sim_time}\nSun position local time: '\
                         + self.settings._dt.sunpos_locTime_str
        return title

    @ staticmethod
    def get_label_and_cm_input(cm_unit, cumulative,
                               df_col_limits: pd.DataFrame = None) -> dict:
        """for the heatmap"""

        # #################################### #
        if cm_unit == 'radiation':
            input_dict = {'colormap': 'inferno'}
            if cumulative:
                # update dict
                dict_up = {'z': 'Whm2', 'z_label':
                           'Cum. Global Ground Irradiation [Wh m$^{-2}$]'
                           }
            else:
                dict_up = {'z': 'Wm2', 'z_label':
                           'Global Ground Irradiance [W m$^{-2}$]'}
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
                           + r' [μmol photons $\cdot$ m$^{-2}]'}
            else:
                dict_up = {'z': 'PARGround', 'z_label': 'PAR'
                           + r' [μmol photons $\cdot$ m$^{-2}\cdot $s$^{-1}$]'}
        # #################################### #
        elif cm_unit == 'DLI':
            input_dict = {'colormap': 'inferno'}
            if cumulative:
                dict_up = {'z': 'DLI', 'z_label':
                           r'DLI [mol photons $\cdot$ m$^{-2}$]'}
            else:
                raise Exception('cm_unit = DLI is only for cumulative')
        else:
            raise Exception('cm_unit has to be radiation, shadow_depth, PAR or DLI')

        input_dict.update(dict_up)

        if df_col_limits is None:
            input_dict['vmin'] = None
            input_dict['vmax'] = None
        else:
            input_dict['vmin'] = df_col_limits.loc['min', input_dict['z']]
            input_dict['vmax'] = df_col_limits.loc['max', input_dict['z']]

        return input_dict
