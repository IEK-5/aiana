# #
# 1. max
# 2. ost mean
# 3. north mean,
# 4. south mean
# #
"""dont do test code outside of if __name__=='__main__'
or it will make problems with multi processing
"""
from apv.classes.weather_data import WeatherData


if __name__ == '__main__':
    import pytictoc
    from pathlib import Path
    import apv
    import os
    from apv.classes.util_classes.sim_datetime import SimDT
    from apv.classes.util_classes.settings_grouper import Settings
    from apv.settings.apv_systems import APV_Syst_InclinedTables_S_Morschenich
    from apv.classes.br_wrapper import BR_Wrapper
    import apv.utils.files_interface as fi

    settings = Settings()
    # ############ SIM SETTINGS #############
    settings.sim.study_name = f'APV_Morschenich_S_inclinedTables'
    settings.sim.scan_position = 'north'
    settings.sim.use_typDay_perMonth_for_irradianceCalculation = True
    settings.sim.use_typDay_perMonth_irradiationData = True
    settings.sim.spatial_resolution = 0.1
    settings.sim.time_step_in_minutes = 5
    settings.sim.TMY_irradiance_aggfunc = 'mean'
    #########################################
    # ########### settings.apv:  ####
    settings.apv = APV_Syst_InclinedTables_S_Morschenich()
    # settings.apv = apv.settings.apv_systems.APV_Morchenich_EastWest()

    # ================== comment this out fo real simulation ==================
    # settings.apv.module_form = 'none'
    # settings.apv.add_airrails = False
    # settings.apv.add_groundScanArea_as_object_to_scene = True
    # ================== =============== ================== ===============

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

    def create_results_subfolder(month, posi):
        return Path(settings.sim.study_name, settings.apv.module_form
                    + f'_res-{settings.sim.spatial_resolution}m'
                    + f'_step-{settings.sim.time_step_in_minutes}min'
                    + f'_TMY_aggfunc-{settings.sim.TMY_irradiance_aggfunc}',
                    f'month-{month}_{posi}-position'  # _correctedSensorOrientation'
                    )

    # only for view_scene, will be overwritten by for loops
    settings.sim.sim_date_time = '06-15_12:00'
    settings.sim.results_subfolder = create_results_subfolder(
        6, settings.sim.scan_position)
    brObj = BR_Wrapper(settings)

    # #
    brObj.octFileObj.create_octfile()
    # #
    brObj.octFileObj.view_octfile(
        view_name='top_down', view_type='parallel'
    )

# #

if __name__ == '__main__':
    months = [6]
    # months = range(1, 13)
    # hours = [19]
    hours = range(2, 24, 1)
    hours = range(7, 13, 1)
    # minutes = [10]
    minutes = range(0, 60, settings.sim.time_step_in_minutes)
    # minutes = range(0, 1, settings.sim.time_step_in_minutes)
    # minute 60 is and has to be exclusive

    enough_light = False  # (for ghi filter)

    for month in months:
        day = 15  # (int(df_all['day_nearest_to_mean'].loc[month]))
        settings.sim.results_subfolder = create_results_subfolder(
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
                        weatherData.daycumulated_ghi * 0.02, 50):
                    print(f'GHI too low ({weatherData.ghi} Wh/m²).')
                    if enough_light is True:
                        settings.sim.enddt = settings.sim.sim_date_time
                        enough_light = False
                else:
                    if enough_light is False:
                        settings.sim.startdt = settings.sim.sim_date_time
                        enough_light = True

                    # to measure elapsed time:
                    tictoc = pytictoc.TicToc()
                    tictoc.tic()
                    # to update time settings in all sub classes of BR_Wrapper:
                    brObj = BR_Wrapper(settings)

                    ########
                    # brObj.octFileObj.create_octfile()

                    # brObj.octFileObj.view_octfile(
                    #    view_name='top_down', view_type='parallel')
                    # brObj.simulate_and_evaluate()
                    ########

                    df_limits = fi.get_min_max_of_cols_in_several_csv_files(
                        [r"C:\Users\l.raumann\Documents\agri-PV\results\APV_Morschenich_S_inclinedTables\std_res-0.1m_step-5min_TMY_aggfunc-mean\month-6_north-position_correctedSensorOrientation\data\ground_results_06-15_07h40.csv",
                         r"C:\Users\l.raumann\Documents\agri-PV\results\APV_Morschenich_S_inclinedTables\std_res-0.1m_step-5min_TMY_aggfunc-mean\month-6_north-position\data\ground_results_06-15_07h40.csv"]).round(1)

                    for cm_unit in ['radiation', 'shadow_depth']:
                        brObj.plotterObj.ground_heatmap(
                            cm_unit=cm_unit,
                            df_col_limits=df_limits
                        )
                    tictoc.toc()


# #
# ======================================================
# cumulate
# ======================================================

# #
if __name__ == '__main__':
    def meta_cumulate(agg_funcs: list, positions: list, equalColLims=False):
        month = 6
        for agg_func in agg_funcs:
            for position in positions:
                settings.sim.scan_position = position
                settings.sim.TMY_irradiance_aggfunc = agg_func
                settings.sim.results_subfolder = create_results_subfolder(
                    month, settings.sim.scan_position)
                # refresh other pathes #TODO |M automate via @property?
                settings.set_names_and_paths()

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
                    settings.paths.csv_parent_folder)

                ##############################################################
                results_folder_cum = \
                    settings.paths.results_folder.parent.parent / 'cumulative'

                fi.make_dirs_if_not_there(results_folder_cum)

                brObj = BR_Wrapper(settings)
                cum_file_name = brObj.plotterObj.return_plot_title(
                    title_comps=['weather', 'position'],
                    cumulative=True)  # +' - month '+str(month)
                cum_file_name = cum_file_name.replace('\n', ' - ').replace(':', '')
                cum_csv_path = results_folder_cum / f'{cum_file_name}.csv'

                if cum_csv_path.exists():  # and not debug_mode...
                    df_merged = fi.df_from_file_or_folder(
                        cum_csv_path)
                else:  # cummulate:
                    df_merged = brObj.evaluatorObj.cumulate_gendaylit_results(
                        settings.paths.csv_parent_folder,
                        cum_csv_path, add_DLI=True
                    )

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
                        cm_unit=cm_unit,
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