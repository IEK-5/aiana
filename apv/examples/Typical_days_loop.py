# #
from apv import resources
from apv.utils import evaluation


if __name__ == '__main__':
    from pathlib import Path
    import pandas as pd
    import importlib as imp
    import apv
    from apv.classes.weather_data import WeatherData
    from apv.classes.sim_datetime import SimDT
    from apv.classes.geometries_handler import GeometriesHandler
    from apv.settings.apv_systems import Default as SystSettings
    from apv.settings import user_pathes

    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.br_wrapper)

    SimSettings = apv.settings.simulation.Simulation()
    APV_SystSettings = apv.settings.apv_systems.Default()
    evalObj = apv.classes.APV_evaluation.APV_Evaluation(
        SimSettings=SimSettings, APV_SystSettings=APV_SystSettings)

    # ### settings:  ####
    SimSettings.sim_name = 'APV_Morschenich'
    APV_SystSettings.module_form = 'std'
    SimSettings.cm_unit = 'radiation'
    SimSettings.spatial_resolution = 0.1
    # SimSettings.use_multi_processing = False
    APV_SystSettings.sceneDict['pitch'] = 12
    # APV_SystSettings.add_groundScanArea_as_object_to_scene = True

    geomObj = GeometriesHandler(SimSettings, APV_SystSettings)

    def modify_APV_SystSettings(APV_SystSettings: SystSettings, hour
                                ) -> SystSettings:
        APV_SystSettings.scene_camera_dicts[
            'top_down']['horizontal_view_angle'] = 80
        APV_SystSettings.scene_camera_dicts[
            'top_down']['vertical_view_angle'] = 50

        # To reduce sim time
        if hour <= 12:
            APV_SystSettings.n_apv_system_clones_in_x = 2
            APV_SystSettings.n_apv_system_clones_in_negative_x = 1
        elif hour > 12:
            APV_SystSettings.n_apv_system_clones_in_x = 1
            APV_SystSettings.n_apv_system_clones_in_negative_x = 2

        return APV_SystSettings

    # To reduce sim time
    y_reduction = (-APV_SystSettings.sceneDict['pitch']*1/2
                   - APV_SystSettings.moduleDict['y'])
    APV_SystSettings.ground_scan_margin_x = 0
    APV_SystSettings.ground_scan_margin_y = y_reduction
    # APV_SystSettings.sceneDict["azimuth"] = 200

    # dummy for path part
    # brObj = apv.br_wrapper.BR_Wrapper(SimSettings, APV_SystSettings)
    # brObj.setup_br()
    # results_path_part: Path = brObj.results_subfolder
    # results_path_part
# #
if __name__ == '__main__':
    months = [6]  # range(1, 13)
    hours = [17]  # range(0, 24, 1)  #

    weatherData = WeatherData(SimSettings)
    df_mean_hours_per_month = weatherData.typical_day_of_month()

    for month in months:
        day = 15  # (int(df_all['day_nearest_to_mean'].loc[month]))
        results_subfolder = user_pathes.results_folder / Path(
            SimSettings.sim_name,
            APV_SystSettings.module_form
            + '_res-' + str(SimSettings.spatial_resolution),
            str(month)
        )

        for hour in hours:
            APV_SystSettings = modify_APV_SystSettings(APV_SystSettings, hour)

            SimSettings.sim_date_time = f'{month}-{day}_{hour}:00'
            simDT = SimDT(SimSettings)
            weatherData.set_dhi_dni_ghi_and_sunpos_to_simDT(simDT)
            hour_utc = simDT.sim_dt_utc.hour

            ghi = df_mean_hours_per_month['GHI'].loc[month, hour_utc]
            dhi = df_mean_hours_per_month['DHI'].loc[month, hour_utc]
            dni = ghi-dhi  # (as ground has tilt 0)

            if weatherData.sunalt < 0:
                print(f'Sun alitude is negative ({weatherData.sunalt}).')
            elif ghi < 50:
                print(f'GHI too low ({ghi} Wh/m²).')
            else:
                brObj = apv.br_wrapper.BR_Wrapper(
                    SimSettings, APV_SystSettings)
                evalObj = apv.classes.APV_evaluation.APV_Evaluation(
                    SimSettings=SimSettings,
                    APV_SystSettings=APV_SystSettings
                )
                brObj.setup_br(dni_singleValue=dni, dhi_singleValue=dhi)
                # brObj.view_scene(view_name='top_down', view_type='parallel')
                brObj.set_up_file_names_and_paths(
                    results_subfolder=results_subfolder
                )
                # brObj.run_raytracing_simulation()
                # brObj.plot_ground_heatmap(cm_unit='shadow_depth')

        SimSettings.startdt = f'{month}-{day}_00:00'
        SimSettings.enddt = f'{month}-{day}_23:00'

        merged_csv_path = results_subfolder / Path(
            'ground_results' + '_cumulative_' + str(month) + '.csv')

        df_merged = evaluation.cumulate_gendaylit_results(
            brObj.csv_parent_folder, merged_csv_path, SimSettings)
        # df_merged = apv.utils.files_interface.df_from_file_or_folder(
        #    merged_csv_path)
        brObj.plot_ground_heatmap(
            df_merged, file_name='cumulative', cumulative=True)

# #

""" for unit...
    for month...
        results_subfolder = user_pathes.results_folder / Path(
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
