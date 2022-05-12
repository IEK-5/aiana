# #
import sys
import pytictoc
import pandas as pd
from pathlib import Path
from typing import Literal

import apv.utils.study_utils as su
import apv.utils.files_interface as fi
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.weather_data import WeatherData
from apv.classes.util_classes.sim_datetime import SimDT
from apv.classes.util_classes.settings_grouper import Settings
from apv.classes.util_classes.geometries_handler import GeometriesHandler

# #
if __name__ == '__main__':
    settings = Settings()
    settings.sim.sim_date_time ='10-15_11:00'
    # #
    subsets = [ #'std',
               # 'std_sw','cell_gaps',
        'checker_board', #'roof_for_EW'
    ]

    for subset in subsets:
        settings = su.adjust_settings(subset, settings)
        brObj = BR_Wrapper(settings)
        brObj.create_and_view_octfile(
            # add_NorthArrow=True,
            # add_groundScanArea=False,
            view_name='as_heatmap'
        )
    # #

if __name__ == '__main__':
    # for subset in ['std_glass', 'roof_for_EW']
    subsets = ['std', 'std_sw', 'checker_board', 'cell_gaps',
               'roof_for_EW']
    subsets = ['cell_gaps']
    months = [4, 6, 8, 10]
    months = [6]
    # months = range(1, 13)
    # hours = [19]
    hours = range(2, 24, 1)
    # hours = range(9, 21, 1)
    # minutes = [10]
    minutes = range(0, 60, settings.sim.time_step_in_minutes)
    # minutes = range(35, 60, settings.sim.time_step_in_minutes)
    # minute 60 is and has to be exclusive

    enough_light = False  # (init value for ghi filter)
    for subset in subsets:
        settings = su.adjust_settings(subset, settings)
        settings = su.adjust_APVclone_count(settings, hours[0])
        # to update time settings in all sub classes of BR_Wrapper:
        brObj = BR_Wrapper(settings)
        brObj.octFileObj.create_octfile_without_sky()
        for month in months:
            day = 15  # (int(df_all['day_nearest_to_mean'].loc[month]))
            settings.sim.results_subfolder = su.create_results_subfolderPath(
                month, settings, subset)

            weatherData = WeatherData(settings)

            for i, hour in enumerate(hours):
                if i > 0:
                    if hour > 13 and hours[i-1] <= 13:
                        settings = su.adjust_APVclone_count(settings, hour)
                        brObj = BR_Wrapper(settings)
                        brObj.octFileObj.create_octfile_without_sky()

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

                        ########
                        brObj.settings.set_names_and_paths()
                        if not brObj.settings.paths.csv_file_path.exists():
                            brObj.update_timeStep(settings)
                            brObj.simulate_and_evaluate()
                        else:
                            print('result exists, skipping')
                            # check if evaluated to avoid 'Wm2' key error
                            df_check: pd.DataFrame = fi.df_from_file_or_folder(
                                brObj.settings.paths.csv_file_path
                            )
                            if 'Wm2' not in df_check.columns:
                                brObj.evaluatorObj.rename_and_add_result_columns()
                        ########

                        # df_limits = fi.get_min_max_of_cols_in_several_csv_files(
                        #    [r"C:\Users\l.raumann\Documents\agri-PV\results\APV_Morschenich_S_inclinedTables\std_res-0.1m_step-5min_TMY_aggfunc-mean\month-6_north-position_correctedSensorOrientation\data\ground_results_06-15_07h40.csv",
                        #     r"C:\Users\l.raumann\Documents\agri-PV\results\APV_Morschenich_S_inclinedTables\std_res-0.1m_step-5min_TMY_aggfunc-mean\month-6_north-position\data\ground_results_06-15_07h40.csv"]).round(1)
                        if month == months[0]:
                            for cm_unit in ['radiation']:
                                fig_path = settings.paths.results_folder / Path(
                                    f'{settings.names.csv_fn[:-4]}_{cm_unit}.jpg')
                                if not fig_path.exists():
                                    brObj.plotterObj.ground_heatmap(
                                        plot_dpi=150,
                                        cm_unit=cm_unit,
                                        # df_col_limits=df_limits
                                    )


# #
# ======================================================
# cumulate and plot cum.
# ======================================================
import pandas as pd
from pathlib import Path

import apv.utils.study_utils as su
import apv.utils.files_interface as fi
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.util_classes.settings_grouper import Settings

if __name__ == '__main__':
    from apv.utils.plotting_utils import plotStyle
    plotStyle(fig_width_in_mm=110)

    settings = Settings()
    dfs = []
    months = [4, 6, 8, 10]
    months = [6]
    subsets = ['std', 'cell_gaps',
               'checker_board',
               'std_sw', 'roof_for_EW'
               ]
    #subsets = ['cell_gaps']
    # for compare_GGI_to in ['GHI_as_TMY_aggfunc', 'clearsky_GHI']:
    for i, subset in enumerate(subsets):
        settings = su.adjust_settings(subset, settings)  # for correct arrow rotation
        compare_GGI_to = 'GHI_as_TMY_aggfunc'
        settings.sim.for_shadowDepths_compare_GGI_to = compare_GGI_to

        for month in months:
            settings.sim.sim_date_time = f'{month:02}-15_12:00'
            # TODO pitfall allert: settings.sim.results_subfolder has to be set again
            settings.sim.results_subfolder = su.create_results_subfolderPath(
                month, settings, subset)

            brObj = BR_Wrapper(settings)
            # def get_cum_csv_path():
            results_folder_cum \
                = brObj.settings.paths.results_folder.parent / 'cumulative'
            fi.make_dirs_if_not_there(results_folder_cum)

            def get_title_and_cum_csv_path(month, compare_GGI_to):
                # - {compare_GGI_to}'
                # +'\ncumulated day (15$^{th}$)' + f' in month {month:02}'
                title = su.titles[subset]
                cum_file_name = subset+'_cumulated day 15th' + f' in month {month:02}'
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

            # """
            path_part = brObj.settings.paths.results_folder.parent.parent/'cumulative_for_poster'
            brObj.plotterObj.ground_heatmap(
                df_merged,
                destination_file_path=path_part/(f'{i}_{subset}.jpg'),
                cumulative=True,
                cm_unit='DLI',
                # cm_unit='shadow_depth',
                plot_title=title,
                north_arrow_xy_posi=(0.05, 1.16),
                col_bar_min=0,
                plot_dpi=400,
                col_bar_max=32,
            )
            # """
        # #

        # #
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
        df = concat_months_for_box_plot(months, compare_GGI_to)
        dfs += [df]
    # fi.df_export(df, )

    # brObj.plotterObj.box_plot_month_comparing(dfs)


# #
# shifeted to comparing_plots/...
# box_plot('shadow_depths_ghi_ref_comparison.jpg', dfs)
