# #
""""""

if __name__ == '__main__':
    from pathlib import Path
    import importlib as imp
    import apv
    from apv.classes.weather_data import WeatherData
    from apv.classes.sim_datetime import SimDT

    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.br_wrapper)

    SimSettings = apv.settings.simulation.Simulation()
    APV_SystSettings = apv.settings.apv_systems.Default()
    evalObj = apv.classes.APV_evaluation.APV_Evaluation(
        SimSettings=SimSettings, APV_SystSettings=APV_SystSettings)

    # ### settings:  ####
    SimSettings.spatial_resolution = 1  # 0.1
    APV_SystSettings.module_form = 'std'
    # To reduce sim time
    y_reduction = (-APV_SystSettings.sceneDict['pitch']/2
                   - APV_SystSettings.moduleDict['y'])
    APV_SystSettings.ground_scan_margin_x = 0  # TODO copy apv system in x
    APV_SystSettings.ground_scan_margin_y = y_reduction
    APV_SystSettings.ground_scan_shift_x = 0
    APV_SystSettings.ground_scan_shift_y = 0

    # APV_SystSettings.sceneDict['nMods'] *= 3
    # APV_SystSettings.n_post_x = 4
    APV_SystSettings.n_sets_x = 3

    # Alternative 1 to filter without exit
    weatherData = WeatherData(SimSettings)
    df_mean_hours_per_month = weatherData.typical_day_of_month()
    months = [6]  # range(1, 13)
    hours = [7]  # range(0, 24, 1)

    brObj = apv.br_wrapper.BR_Wrapper(
        SimSettings=SimSettings,
        APV_SystSettings=APV_SystSettings
    )
    # #
    brObj.setup_br()
    brObj.view_scene()
# #
if __name__ == '__main__':
    for month in months:
        day = 15  # (int(df_all['day_nearest_to_mean'].loc[month]))
        for hour in hours:
            SimSettings.sim_date_time = f'{month}-{day}_{hour}h'
            simDT = SimDT(SimSettings)
            weatherData.set_dhi_dni_ghi_and_sunpos_to_simDT(simDT)
            hour_utc = simDT.sim_dt_utc.hour

            ghi = df_mean_hours_per_month['GHI'].loc[month, hour_utc]
            dhi = df_mean_hours_per_month['DHI'].loc[month, hour_utc]
            dni = ghi-dhi  # (as ground has tilt 0)
            # print(f'GHI: {ghi}, sunalt: {weatherData.sunalt}.')
            if weatherData.sunalt < 0:
                print(f'Sun alitude is negative ({weatherData.sunalt}).')
            elif ghi < 50:
                print(f'GHI too low ({ghi} Wh/m²).')
            else:
                SimSettings.sim_name = (
                    f'APV_Morschenich_{APV_SystSettings.module_form}'
                    f'_res_{SimSettings.spatial_resolution}'
                    f'_{SimSettings.sim_date_time}')

                brObj = apv.br_wrapper.BR_Wrapper(
                    SimSettings=SimSettings,
                    APV_SystSettings=APV_SystSettings
                )
                evalObj = apv.classes.APV_evaluation.APV_Evaluation(
                    SimSettings=SimSettings,
                    APV_SystSettings=APV_SystSettings
                )
                brObj.setup_br(dni_singleValue=dni, dhi_singleValue=dhi)
                brObj.view_scene()
                # brObj.run_raytracing_simulation()
                # brObj.plot_ground_insolation()

    # #
    evalObj.evaluate_APV()
