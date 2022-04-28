# #
import sys
import seaborn as sns
from typing import Literal
from matplotlib import pyplot as plt
import pandas as pd
from apv.classes.weather_data import WeatherData
import pytictoc
from pathlib import Path
import os
from apv.classes.util_classes.sim_datetime import SimDT
from apv.classes.util_classes.settings_grouper import Settings
from apv.settings.apv_systems import APV_Syst_InclinedTables_S_Morschenich
from apv.classes.br_wrapper import BR_Wrapper
from apv.utils import plotting_utils
import apv.utils.files_interface as fi
from apv.classes.util_classes.geometries_handler import GeometriesHandler


def set_settings(
        subset: Literal['std', 'std_glass', 'std_sw',
                        'checker_board', 'cell_gaps', 'roof_for_EW'],
        settings: Settings) -> Settings:
    # constant settings
    settings.sim.study_name = 'framed_APV_noBorderEffects'
    settings.sim.spatial_resolution = 0.25
    settings.sim.time_step_in_minutes = 6
    settings.sim.use_acceleradRT_view = True
    settings.sim.use_accelerad_GPU_processing = True

    ghObj = GeometriesHandler(settings)
    # name depending settings
    settings.apv.glass_modules = False
    settings.apv.module_form = 'std'
    settings.apv.sceneDict['nRows'] = 6
    settings.apv.sceneDict['azimuth'] = 180
    settings.apv.mountingStructureDict.update({
        'n_apv_system_clones_in_x': 3,
        'n_apv_system_clones_in_negative_x': 3})
    settings.apv.gScan_area.update({
        'ground_scan_margin_y': -2*settings.apv.sceneDict['pitch']
        - ghObj.singleRow_footprint_y/2,
        'ground_scan_shift_y': settings.apv.sceneDict['pitch']
        + settings.apv.mountingStructureDict['post_thickness_y']/2,
    })

    if subset == 'std_sw':
        settings.apv.sceneDict['azimuth'] = 225

    elif subset == 'roof_for_EW':
        settings.apv.module_form = 'roof_for_EW'
        settings.apv.sceneDict['azimuth'] = 90
        settings.apv.sceneDict['nRows'] = 8
        settings.apv.sceneDict['nRows'] = 8
        # TODO x and y scale need to be swapped to be strict?
        settings.apv.gScan_area.update({
            'ground_scan_margin_y': -3*settings.apv.sceneDict['pitch']
            - ghObj.singleRow_footprint_y/2,
            'ground_scan_shift_x': ghObj.scan_length_x,
            'ground_scan_shift_y': 0})
        settings.apv.mountingStructureDict.update({
            'n_apv_system_clones_in_x': 2,
            'n_apv_system_clones_in_negative_x': 2})

    elif subset == 'std_glass':
        settings.apv.glass_modules = True

    elif subset == 'checker_board':
        settings.apv.glass_modules = True
        settings.apv.module_form = 'cell_level_checker_board'
        settings.apv.cellLevelModuleParams.update({
            'xcellgap': 0, 'ycellgap': 0
        })

    elif subset == 'cell_gaps':
        settings.apv.glass_modules = True
        settings.apv.module_form = 'cell_level'
        settings.apv.cellLevelModuleParams.update({
            'xcellgap': 0.02, 'ycellgap': 0.02
        })
    elif subset is not 'std':
        sys.exit('This subset does not exist.')
    return settings


if __name__ == '__main__':
    subset = 'std_glass'
    #subset = 'std'
    settings = Settings()
    settings = set_settings(subset, settings)
    brObj = BR_Wrapper(settings)

    def create_results_subfolderPath(month):
        return Path(
            settings.sim.study_name, subset
            + f'_res-{settings.sim.spatial_resolution}m'
            + f'_step-{settings.sim.time_step_in_minutes}min',
            f'month-{month}'
        )
    # #
    brObj.create_and_view_octfile(add_NorthArrow=True)
# #
# simulate
if __name__ == '__main__':
    # for subset in ['std_glass', 'roof_for_EW']

    months = [6, 8, 10, 12]
    months = [12]
    # months = range(1, 13)
    # hours = [19]
    hours = range(2, 24, 1)
    # hours = range(16, 21, 1)
    # minutes = [10]
    minutes = range(0, 60, settings.sim.time_step_in_minutes)
    # minutes = range(35, 60, settings.sim.time_step_in_minutes)
    # minute 60 is and has to be exclusive

    enough_light = False  # (init value for ghi filter)

    for month in months:
        day = 15  # (int(df_all['day_nearest_to_mean'].loc[month]))
        settings.sim.results_subfolder = create_results_subfolderPath(
            month)

        weatherData = WeatherData(settings)

        for hour in hours:
            for minute in minutes:
                # set time with leading zeros for a correct file order
                settings.sim.sim_date_time = \
                    f'{month:02}-{day}_{hour:02}:{minute:02}'

                # ghi filter and setting start and end dt for plot title
                weatherData.set_dhi_dni_ghi_and_sunpos_to_simDT(
                    SimDT(settings.sim))
                if (weatherData.sunalt < 0):
                    print(f'Sun alitude < 0 ({weatherData.sunalt}).')
                elif weatherData.ghi < min(
                        weatherData.cumulated_ghi * 0.02, 50):
                    print(f'GHI too low ({weatherData.ghi} Wh/m²).')
                    if enough_light is True:
                        settings.sim.enddt = settings.sim.sim_date_time
                        enough_light = False
                else:
                    if enough_light is False:
                        settings.sim.startdt = settings.sim.sim_date_time
                        enough_light = True

                    # to update time settings in all sub classes of BR_Wrapper:
                    brObj = BR_Wrapper(settings)

                    ########
                    if not brObj.settings.paths.csv_file_path.exists():
                        brObj.octFileObj.create_octfile()
                        brObj.simulate_and_evaluate()
                    else:
                        print('result exists, skipping')
                    ########

                    # df_limits = fi.get_min_max_of_cols_in_several_csv_files(
                    #    [r"C:\Users\l.raumann\Documents\agri-PV\results\APV_Morschenich_S_inclinedTables\std_res-0.1m_step-5min_TMY_aggfunc-mean\month-6_north-position_correctedSensorOrientation\data\ground_results_06-15_07h40.csv",
                    #     r"C:\Users\l.raumann\Documents\agri-PV\results\APV_Morschenich_S_inclinedTables\std_res-0.1m_step-5min_TMY_aggfunc-mean\month-6_north-position\data\ground_results_06-15_07h40.csv"]).round(1)
                    # """
                    for cm_unit in ['radiation']:
                        brObj.plotterObj.ground_heatmap(
                            plot_dpi=100,
                            cm_unit=cm_unit,
                            # df_col_limits=df_limits
                        )
                    # """

# #
# ======================================================
# cumulate
# ======================================================

if __name__ == '__main__':
    dfs = []
    for compare_GGI_to in ['GHI_as_TMY_aggfunc', 'clearsky_GHI']:
        settings.sim.for_shadowDepths_compare_GGI_to = compare_GGI_to

        for month in [6, 8, 10, 12]:
            # for month in [12]:
            settings.sim.sim_date_time = f'{month:02}-15_12:00'
            # TODO pitfall allert: settings.sim.results_subfolder has to be set again
            settings.sim.results_subfolder = create_results_subfolderPath(month)

            brObj = BR_Wrapper(settings)
            # def get_cum_csv_path():
            results_folder_cum \
                = brObj.settings.paths.results_folder.parent / 'cumulative'
            fi.make_dirs_if_not_there(results_folder_cum)

            def get_title_and_cum_csv_path(month, compare_GGI_to):
                title = 'cumulated day (15$^{th}$)' + f' in month {month:02} - {compare_GGI_to}'
                cum_file_name = title.replace('(15$^{th}$)', '15th')
                cum_csv_path = results_folder_cum / f'{cum_file_name}.csv'
                return title, cum_csv_path

            def get_df_merged(cum_csv_path: Path):
                if cum_csv_path.exists():  # and not debug_mode...
                    return fi.df_from_file_or_folder(cum_csv_path)
                else:  # cummulate:
                    print(cum_csv_path, ' not found, cumulating...\n')
                    # TODO speed up? cant append blindly directly after sim, as want to be able to redo only certain time steps
                    return brObj.evaluatorObj.cumulate_gendaylit_results(
                        brObj.settings.paths.csv_parent_folder,
                        cum_csv_path, add_DLI=True
                    )

            title, cum_csv_path = get_title_and_cum_csv_path(month, compare_GGI_to)
            df_merged = get_df_merged(cum_csv_path)
            # brObj.plotterObj.ground_heatmap(cumulative=True) #TODO alow this way

            #"""
            brObj.plotterObj.ground_heatmap(
                df_merged,
                destination_file_path=Path(str(cum_csv_path).replace('csv', 'jpg')),
                cumulative=True,
                # cm_unit='DLI',
                cm_unit='shadow_depth',
                plot_title=title,
                north_arrow_xy_posi=(-0.14, 1.16),
                col_bar_min=0,
                # col_bar_max=32,
            )
            #"""

        def concat_months_for_box_plot(months: list, compare_GGI_to):
            """input: months list: as ints
            """
            df_appended = pd.DataFrame()

            for month in months:
                title, cum_csv_path = get_title_and_cum_csv_path(month, compare_GGI_to)
                df = fi.df_from_file_or_folder(cum_csv_path)
                df['Month'] = month

                df = df[df['ShadowDepth_cum'] < 98]
                df_appended = pd.concat([df_appended, df])
                df_appended.name = compare_GGI_to
            fi.df_export(df_appended, results_folder_cum/f'appended_{compare_GGI_to}.csv')
            return df_appended
        df = concat_months_for_box_plot([6, 8, 10, 12], compare_GGI_to)
        dfs += [df]
    # fi.df_export(df, )

    # brObj.plotterObj.box_plot_month_comparing(dfs)


# #
# shifeted to comparing_plots/...
# box_plot('shadow_depths_ghi_ref_comparison.jpg', dfs)
