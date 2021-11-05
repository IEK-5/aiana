# #
if __name__ == '__main__':
    from pathlib import Path
    import pandas as pd
    import importlib as imp
    import apv
    from apv.classes.weather_data import WeatherData
    from apv.classes.sim_datetime import SimDT
    from apv.classes.geometries_handler import GeometriesHandler
    from apv.settings.apv_systems import Default as SystSettings
    from apv.settings import user_paths

    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.br_wrapper)

    # ############ SIM SETTINGS #############
    SimSettings = apv.settings.simulation.Simulation()
    # SimSettings.sim_name = 'APV_Morschenich_only_one_neighborset'
    SimSettings.sim_name = 'APV_Morschenich'
    SimSettings.use_typical_day_per_month_for_shadow_depth_calculation = True
    SimSettings.spatial_resolution = 0.25
    SimSettings.time_step_in_minutes = 6  # 6
    # SimSettings.use_multi_processing = False
    #########################################

    # ### APV_SystSettings:  ####
    APV_SystSettings = apv.settings.apv_systems.APV_Morchenich_Checkerboard()
    APV_SystSettings.module_form = 'std'
    # APV_SystSettings = apv.settings.apv_systems.APV_Morchenich_EastWest()
    # APV_SystSettings.module_form = 'none'
    APV_SystSettings.add_groundScanArea_as_object_to_scene = True

    def adjust_APVclone_position(APV_SystSettings: SystSettings, hour
                                 ) -> SystSettings:
        # To reduce sim time
        if hour <= 12:
            APV_SystSettings.n_apv_system_clones_in_x = 3  # old: 2, new: 3,
            APV_SystSettings.n_apv_system_clones_in_negative_x = 1  # 1
        elif hour > 12:
            APV_SystSettings.n_apv_system_clones_in_x = 1  # 1
            APV_SystSettings.n_apv_system_clones_in_negative_x = 3  # 2 or 3

        return APV_SystSettings

    # APV_SystSettings.sceneDict["azimuth"] = 200

    # dummy for path part
    # brObj = apv.br_wrapper.BR_Wrapper(SimSettings, APV_SystSettings)
    # brObj.setup_br()
    # results_path_part: Path = brObj.results_subfolder
    # results_path_part

if __name__ == '__main__':
    ###########################################################################
    setup_br_and_simulate = True
    ###########################################################################
    months = range(1, 13)
    hours = range(0, 24, 1)  #
    minutes = range(0, 60, SimSettings.time_step_in_minutes)  # [0]  #
    appended_data = []
    # minute 60 is and has to be exclusive

    weatherData = WeatherData(SimSettings)
    df_typic_day_of_month = weatherData.typical_day_of_month(
        weatherData.df_irradiance)

    brObj = apv.br_wrapper.BR_Wrapper(
        SimSettings, APV_SystSettings,
        weatherData=weatherData)

    sun_shines = False
    for month in months:
        day = 15  # (int(df_all['day_nearest_to_mean'].loc[month]))

        cumulative_GHI = weatherData.df_irradiance_typ_day_per_month.loc[
            (month), 'ghi_Whm-2'].sum()

        subfolder: Path = Path(
            SimSettings.sim_name,
            APV_SystSettings.module_form
            + '_res-' + str(SimSettings.spatial_resolution)+'m'
            + '_step-' + str(SimSettings.time_step_in_minutes)+'min',
            str(month)
        )
        brObj.results_subfolder = user_paths.results_folder / subfolder

        # for hour in hours:
        #     if APV_SystSettings.module_form in [
        #             'std', 'cell_level_checker_board']:
        #         APV_SystSettings = adjust_APVclone_position(
        #             APV_SystSettings, hour
        #         )
        #     geomObj = GeometriesHandler(SimSettings, APV_SystSettings)
        #     # TODO syst cloning should be called also in geometries handler
        #     # and not in br_wrapper
        #     for minute in minutes:
        #         # for optical reasons only:
        #         min_str = str(minute)
        #         if minute < 10:
        #             min_str = "0"+min_str

        #         SimSettings.sim_date_time = f'{month}-{day}_{hour}:{min_str}'
        #         simDT = SimDT(SimSettings)

        #         hour_utc = simDT.sim_dt_utc.hour
        #         ghi = df_typic_day_of_month['ghi_Wm-2'].loc[
        #             month, hour_utc, minute]
        #         dhi = df_typic_day_of_month['dhi_Wm-2'].loc[
        #             month, hour_utc, minute]

        #         dni = ghi-dhi  # (as ground has tilt 0)
        #         weatherData.set_dhi_dni_ghi_and_sunpos_to_simDT(simDT)

        #         if (weatherData.sunalt < 0):
        #             print(f'Sun alitude is negative ({weatherData.sunalt}).')
        #         # elif (ghi < cumulative_GHI * 0.02) or (ghi > 50):
        #         elif ghi < min(cumulative_GHI * 0.02, 50):

        #             print(f'GHI too low ({ghi} Wh/m²).')
        #             if sun_shines is True:
        #                 SimSettings.enddt = SimSettings.sim_date_time
        #                 sun_shines = False
        #         else:
        #             if sun_shines is False:
        #                 SimSettings.startdt = SimSettings.sim_date_time
        #                 sun_shines = True

        #             brObj.SimSettings = SimSettings
        #             if setup_br_and_simulate:
        #                 brObj.setup_br(
        #                     dni_singleValue=dni, dhi_singleValue=dhi)
        #                 # brObj.view_scene(
        #                 # view_name='top_down', view_type='parallel')
        #                 ########
        #                 brObj.run_raytracing_simulation()
        #                 ########
        #                 for cm_unit in ['radiation', 'shadow_depth']:
        #                     brObj.plot_ground_heatmap(cm_unit=cm_unit)

        results_subfolder_cum = user_paths.results_folder / Path(
            subfolder.parent, 'cumulative_hours_in_typ_day_of_month')

        apv.utils.files_interface.make_dirs_if_not_there(results_subfolder_cum)
        cum_file_name = 'ground_results' + '_cumulative_' + str(month)
        cum_csv_path = results_subfolder_cum / Path(cum_file_name + '.csv')

        # # TODO was muss wirklich neu gesetzt werden?
        # # oder arbeiten wir lieber mit zwangsübergabe ohne default settings?
        # brObj.evalObj.SimSettings = SimSettings  # wahrscheinlich unnötig

        # df_merged = brObj.evalObj.cumulate_gendaylit_results(
        #     brObj.results_subfolder / Path('data'), cum_csv_path, SimSettings)
        df_merged = apv.utils.files_interface.df_from_file_or_folder(
            cum_csv_path)
        # for cm_unit in ['radiation', 'shadow_depth', 'DLI']:
        #     brObj.plot_ground_heatmap(
        #         df_merged, file_name=cum_file_name,
        #         destination_folder=results_subfolder_cum,
        #         cumulative=True,
        #         cm_unit=cm_unit
        #     )

        # Merge monthly data for comparison plot plotting
        df_merged['Month'] = month
        appended_data.append(df_merged)
    # Concatenate all monthly data
    appended_data = pd.concat(appended_data)
    # #
    print(appended_data)
    # #
    # Create DataFrame of monthly average and std
    avg_std_df = brObj.evalObj.monthly_avg_std(data=appended_data,
                                               column='ShadowDepth_cum',
                                               group_by='Month')

    print(avg_std_df)
    # Create Ridge Plot
    # #
    fig, axes = apv.utils.plots.Ridge_plot(data=appended_data,
                                           seperate_by='Month',
                                           column='ShadowDepth_cum')
    apv.utils.files_interface.save_fig(
        fig=fig,
        file_name=f'Ridgeplot_ShadowDepth2_{APV_SystSettings.module_form}_' +
        f'{SimSettings.spatial_resolution}m_' +
        f'{SimSettings.time_step_in_minutes}_min',
        parent_folder_path=results_subfolder_cum.parent)

# #
""" for unit...
    for month...
        results_subfolder = user_paths.results_folder / Path(
            SimSettings.sim_name,
            APV_SystSettings.module_form
            + '_res-' + str(SimSettings.spatial_resolution),
            str(month)
        )
        merged_csv_path = results_subfolder / Path(
            'ground_results' + '_cumulative_' + str(month) + '.csv')
        df_merged = apv.utils.files_interface.df_from_file_or_folder(
                merged_csv_path)
        brObj.plot_ground_heatmap(
            df_merged, file_name='cumulative', cumulative=True) """
