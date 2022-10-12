# #

"""dont do test code outside of if __name__=='__main__'
or it will make problems with multi processing
"""
from apv.classes.weather_data import WeatherData
import pytictoc
from pathlib import Path
import os
from apv.classes.util_classes.sim_datetime import SimDT
from apv.classes.util_classes.settings_handler import Settings
from apv.settings.apv_system_settings import APV_Syst_InclinedTables_S_Morschenich
from apv.classes.br_wrapper import BR_Wrapper
import apv.utils.files_interface as fi

if __name__ == '__main__':
    settings = Settings()
    # ############ SIM SETTINGS #############
    settings.sim.sub_study_name = f'APV_Morschenich_S_inclinedTables'
    # settings.sim.scan_position = 'north'
    settings.sim.plot_title_components = [
        # 'weather', 'position',
        'datetime'
    ]
    settings.sim.use_typDay_perMonth_for_irradianceCalculation = True
    settings.sim.spatial_resolution = 0.04
    settings.sim.time_step_in_minutes = 2
    settings.sim.TMY_irradiance_aggfunc = 'mean'

    settings.sim.use_accelerad_GPU_processing = True

    #########################################
    # ########### settings.apv:  ####
    settings.apv = APV_Syst_InclinedTables_S_Morschenich()
    # settings.apv = apv.settings.apv_systems.APV_Morchenich_EastWest()

    # ================== comment this out fo real simulation ==================
    # settings.apv.module_form = 'none'
    # settings.apv.add_airrails = False
    # settings.apv.add_groundScanArea_as_object_to_scene = True
    # ================== =============== ================== ===============

    """
    x_reduction = -((settings.apv.moduleDict['x']
                     + settings.apv.moduleDict['xgap'])
                    * (settings.apv.sceneDict['nMods']))/2+2  # =2*2m=4m
    y_reduction = (-settings.apv.sceneDict['pitch']
                   - settings.apv.moduleDict['y']/2)
    settings.apv.ground_scan_margin_x = x_reduction  # -3
    settings.apv.ground_scan_margin_y = y_reduction  # -32
    # -32
    settings.apv.ground_scan_shift_x = 2 + \
        settings.sim.plots_shifts_xy[settings.sim.scan_position][0]*4
    settings.apv.ground_scan_shift_y = \
        settings.apv.sceneDict['pitch'] \
        * settings.sim.plots_shifts_xy[settings.sim.scan_position][1]\
        + settings.apv.mountingStructureDict['inner_table_post_distance_y']
    """
    settings.apv.gScanAreaDict['ground_scan_margin_x'] = -10.5
    settings.apv.gScanAreaDict['ground_scan_shift_x'] = 10.5

    def create_results_subfolderPath(month, posi):
        return Path(
            settings.sim.sub_study_name, settings.apv.module_form
            + f'_res-{settings.sim.spatial_resolution}m'
            + f'_step-{settings.sim.time_step_in_minutes}min'
            + f'_TMY_aggfunc-{settings.sim.TMY_irradiance_aggfunc}',
            f'month-{month}'  # _{posi}-position'  # _correctedSensorOrientation'
        )

    # only for view_scene, will be overwritten by for loops
    month = 4
    settings.sim.sim_date_time = f'{month:02}-15_12:00'
    settings.sim.results_subfolder = create_results_subfolderPath(
        month, settings.sim.scan_position)

    # #
    backup = settings.sim.spatial_resolution
    settings.sim.spatial_resolution = 1
    BR_Wrapper(settings).create_and_view_octfile_for_SceneInspection(  # topDownParallel_view=True
    )
    settings.sim.spatial_resolution = backup

# #

if __name__ == '__main__':
    months = [4]
    # months = range(1, 13)
    # hours = [19]
    hours = range(2, 24, 1)
    #hours = range(20, 21, 1)
    # minutes = [10]
    minutes = range(0, 60, settings.sim.time_step_in_minutes)
    #minutes = range(35, 60, settings.sim.time_step_in_minutes)
    # minute 60 is and has to be exclusive

    enough_light = False  # (init value for ghi filter)

    for month in months:
        day = 15  # (int(df_all['day_nearest_to_mean'].loc[month]))
        settings.sim.results_subfolder = create_results_subfolderPath(
            month, settings.sim.scan_position)

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
                        weatherData.dailyCumulated_ghi * 0.02, 50):
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
                    brObj.octFileObj.create_octfile_without_sky()
                    brObj.simulate_and_evaluate()
                    ########

                    # df_limits = fi.get_min_max_of_cols_in_several_csv_files(
                    #    [r"C:\Users\l.raumann\Documents\agri-PV\results\APV_Morschenich_S_inclinedTables\std_res-0.1m_step-5min_TMY_aggfunc-mean\month-6_north-position_correctedSensorOrientation\data\ground_results_06-15_07h40.csv",
                    #     r"C:\Users\l.raumann\Documents\agri-PV\results\APV_Morschenich_S_inclinedTables\std_res-0.1m_step-5min_TMY_aggfunc-mean\month-6_north-position\data\ground_results_06-15_07h40.csv"]).round(1)

                    for cm_unit in ['radiation']:
                        brObj.plotterObj.ground_heatmap(
                            cm_quantity=cm_unit,
                            # df_col_limits=df_limits
                        )


# #
# ======================================================
# cumulate
# ======================================================

# simple

if __name__ == '__main__':
    month = 6
    settings.sim.plot_dpi = 600
    settings.sim.sim_date_time = f'{month:02}-15_12:00'
    # TODO pitfall allert: settings.sim.results_subfolder has to be set again
    settings.sim.results_subfolder = create_results_subfolderPath(
        month, settings.sim.scan_position)

    brObj = BR_Wrapper(settings)
    # def get_cum_csv_path():
    results_folder_cum \
        = brObj.settings._paths.results_folder.parent.parent / 'cumulative'
    fi.make_dirs_if_not_there(results_folder_cum)

    cum_file_name = brObj.plotterObj.return_plot_title(
        title_comps=['datetime', 'resolution'],
        # title_comps=['weather', 'position'],
        cumulative=True)  # +' - month '+str(month)
    cum_file_name = cum_file_name.replace('\n', ' - ').replace(':', '')
    title = 'cumulated day (15$^{th}$)' + f' in month {month}'
    cum_file_name = title.replace('(15$^{th}$)', '15th')
    cum_csv_path = results_folder_cum / f'{cum_file_name}.csv'

    def get_df_merged(cum_csv_path: Path):
        if cum_csv_path.exists():  # and not debug_mode...
            return fi.df_from_file_or_folder(cum_csv_path)
        else:  # cummulate:
            print(cum_csv_path, ' not found, cumulating...\n')
            # TODO speed up? cant append blindly directly after sim, as want to be able to redo only certain time steps
            return brObj.evaluatorObj.cumulate_gendaylit_results(
                brObj.settings._paths.inst_csv_parent_folder,
                cum_csv_path, add_DLI=True
            )
    df_merged = get_df_merged(cum_csv_path)
    # brObj.plotterObj.ground_heatmap(cumulative=True) #TODO alow this way

    brObj.plotterObj.ground_heatmap(
        df_merged,
        destination_file_path=Path(str(cum_csv_path).replace('csv', 'jpg')),
        cumulative=True,
        cm_quantity='DLI',
        plot_title=title,
        north_arrow_xy_posi=(-0.14, 1.16),
        col_bar_min=0,
        col_bar_max=32,
    )
# #
test = df_merged.sort_values(by=['y', 'x'])
test.agg([min, max])
# #
# complex
if __name__ == '__main__':
    def meta_cumulate(agg_funcs: list, positions: list, equalColLims=False):
        month = 6
        for agg_func in agg_funcs:
            for position in positions:
                settings.sim.scan_position = position
                settings.sim.TMY_irradiance_aggfunc = agg_func
                settings.sim.results_subfolder = create_results_subfolderPath(
                    month, settings.sim.scan_position)
                # refresh other pathes #TODO |M automate via @property?
                settings.update_sim_dt_and_paths()

                def get_date_time_str(file_name: str) -> str:
                    string_parts = file_name[:-4].replace('h', ':').split('_')
                    return f'{string_parts[2]}_{string_parts[3]}'

                def set_startdt_and_enddt(folder_path: Path):
                    """for plot title and daily cumulated shadow_depth-
                    reference-GHI
                    """
                    file_list = os.listdir(str(folder_path))
                    settings.sim.startdt = get_date_time_str(file_list[0])
                    # testing same times for ghi clear sky cum
                    # settings.sim.startdt = '6-15_06:15'

                    # TODO get_date_time_str(file_list[-1]) + time_step_in_minutes...
                    enddts = {'min': '6-15_20:00', 'mean': '6-15_20:50',
                              'max': '6-15_21:00'}
                    settings.sim.enddt = enddts[agg_func]

                set_startdt_and_enddt(
                    settings._paths.inst_csv_parent_folder)

                ##############################################################

                cum_csv_path = get_cum_csv_path()
                df_merged = get_df_merged(cum_csv_path)

                # gather file pathes to get min, max  for equal color maps
                csv_files = []
                if len(agg_funcs) > 1:
                    heatmap_subfolder = f'weather-variation position-{position}'
                    for weather in ['clear sky', 'mean cloudy', 'max cloady']:
                        csv_files += [str(cum_csv_path).replace(
                            brObj.plotterObj.return_weather_description(), weather)]
                if len(positions) > 1:
                    heatmap_subfolder = f'position-variation weather-mean'
                    for posi2 in positions:
                        csv_files += [
                            str(cum_csv_path).replace(position, posi2)]

                # plot
                if equalColLims:
                    folder_extension = '_equalColLimits'
                    df_limits = fi.get_min_max_of_cols_in_several_csv_files(
                        csv_files).round(1)
                else:
                    folder_extension = ''
                    df_limits = None

                for cm_unit in ['shadow_depth',
                                'radiation', 'DLI'
                                ]:
                    file_path = results_folder_cum / Path(
                        f'{heatmap_subfolder}{folder_extension}',
                        f'{cum_file_name}_{cm_unit}.jpg'
                    )
                    brObj.plotterObj.ground_heatmap(
                        df_merged,
                        destination_file_path=file_path,
                        cumulative=True,
                        cm_quantity=cm_unit,
                        df_col_limits=df_limits
                    )

    all_aggs = ['min', 'mean', 'max']
    all_positions = ['south', 'center', 'east', 'north']
    meta_cumulate(agg_funcs=all_aggs, positions=['center'])
    meta_cumulate(agg_funcs=['mean'], positions=all_positions)
    meta_cumulate(agg_funcs=all_aggs, positions=['center'], equalColLims=True)
    # #
    meta_cumulate(
        agg_funcs=['mean'], positions=all_positions, equalColLims=True)

# #
