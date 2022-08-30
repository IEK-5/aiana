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
    # #
    subsets = [  # 'std',
        'cell_gaps',
        # 'cell_gaps',
        # 'checker_board',  # 'roof_for_EW'
    ]

    for subset in subsets:
        settings = su.adjust_settings(subset, settings)
        settings.sim.sim_date_time = '4-15_09:00'
        settings.sim.spatial_resolution = 0.5
        brObj = BR_Wrapper(settings)
        brObj.create_and_view_octfile_for_SceneInspection(
            # add_NorthArrow=True,
            # add_groundScanArea=False,
            # view_name='top_down'
        )
    # #

if __name__ == '__main__':
    limit_root = r"C:\Users\Leonard Raumann\Documents\agri-PV\results\framed_APV_noBorderEffects\res-0.05m_step-3min\checker_board\month-6\data"
    df_limits = fi.get_min_max_of_cols_in_several_csv_files(
        [limit_root+r"\ground_results_06-15_06h27.csv",
         limit_root+r"\ground_results_06-15_13h15.csv"]).round(1)
    # for subset in ['std_glass', 'roof_for_EW']
    subsets = ['std',
               'std_sw', 'checker_board', 'cell_gaps',
               'roof_for_EW']
    subsets = ['std']
    months = [4, 6, 8, 10]
    months = [4]
    # months = range(1, 13)
    # hours = [19]
    hours = range(2, 24, 1)
    #hours = range(2, 12, 1)
    # minutes = [10]
    minutes = range(0, 60, settings.sim.time_step_in_minutes)
    minutes = [0]
    # minutes = range(35, 60, settings.sim.time_step_in_minutes)
    # minute 60 is and has to be exclusive

    enough_light = False  # (init value for ghi filter)
    for subset in subsets:
        settings = su.adjust_settings(subset, settings)
        settings = su.adjust_APVclone_count(settings, hours[0])
        settings.sim.rtraceAccuracy = 'accurate'
        # to update time settings in all sub classes of BR_Wrapper:
        brObj = BR_Wrapper(settings)
        brObj.octFileObj.create_octfile_without_sky()
        for month in months:
            day = 15  # (int(df_all['day_nearest_to_mean'].loc[month]))
            settings.sim.results_subfolder: Path = su.create_results_subfolderPath(
                month, settings, subset) / settings.sim.rtraceAccuracy

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
                            weatherData.dailyCumulated_ghi * 0.02, 50):
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
                            brObj.update_timeStep_and_sky(settings)
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

                        if month in months:  # == months[0]:
                            for cm_unit in ['radiation']:
                                fig_path = settings.paths.results_folder / Path(
                                    f'{settings.names.csv_fn_ext[:-4]}_{cm_unit}.jpg')
                                if not fig_path.exists():
                                    brObj.plotterObj.ground_heatmap(
                                        plot_dpi=250,
                                        cm_quantity=cm_unit,
                                        df_col_limits=df_limits
                                    )

# #
settings.sim.time_step_in_minutes
# #
# ======================================================
# cumulate and plot cum.
# ======================================================


if __name__ == '__main__':
    from apv.utils.plotting_utils import plotStyle
    plotStyle(fig_width_in_mm=80)

    settings = Settings()
    dfs = []
    months = [4, 6, 8, 10]
    months = [4]
    subsets = ['std', 'cell_gaps',
               'checker_board',
               'std_sw', 'roof_for_EW'
               ]
    subsets = ['cell_gaps']
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

            results_folder_cum \
                = brObj.settings.paths.results_folder.parent / 'cumulative'
            fi.make_dirs_if_not_there(results_folder_cum)

            cum_csv_path = su.get_cum_csv_path(
                month, subset, results_folder_cum,  # compare_GGI_to
            )

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
            df_merged = get_df_merged(cum_csv_path)
            # brObj.plotterObj.ground_heatmap(cumulative=True) #TODO alow this way

            # """
            desti_fp = Path(str(cum_csv_path).replace('csv', 'jpg'))
            desti_fp = Path(r'T:\Public\user\l.raumann_network\agri-PV\Poster'
                            )/(f'{i}_{subset}.jpg')
            brObj.plotterObj.ground_heatmap(
                df_merged,
                destination_file_path=desti_fp,
                cumulative=True,
                cm_quantity='DLI',
                # cm_unit='shadow_depth',
                # +'\ncumulated day (15$^{th}$)' + f' in month {month:02}'
                plot_title=su.titles[subset],
                north_arrow_xy_posi=(0.05, 1.18),
                col_bar_min=0,
                plot_dpi=400,
                col_bar_max=32,
            )
            # """
        # #

        # #


# #
# shifeted to comparing_plots/...
# box_plot('shadow_depths_ghi_ref_comparison.jpg', dfs)
