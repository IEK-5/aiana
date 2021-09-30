# #
"""apv main"""

if __name__ == '__main__':
    from pathlib import Path
    import importlib as imp
    import apv
    from apv.utils.weather_data import WeatherData

    imp.reload(apv.utils.GeometriesHandler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.br_wrapper)

    SimSettings = apv.settings.simulation.Simulation()
    APV_SystSettings = apv.settings.apv_systems.Default()
    evalObj = apv.utils.APV_evaluation.Evaluate_APV(
        SimSettings=SimSettings, APV_SystSettings=APV_SystSettings)
    weatherObj = WeatherData()
    # ### settings:  ####
    SimSettings.spatial_resolution = 0.1
    SimSettings.sky_gen_mode = 'gendaylit'
    SimSettings.irradiance_data_source = 'ADS_satellite'
    APV_SystSettings.module_form = 'std'
    # To reduce sim time
    APV_SystSettings.ground_scan_margin_x = 4
    APV_SystSettings.ground_scan_margin_y = 2
    weather_file = apv.settings.user_pathes.bifacial_radiance_files_folder / \
        Path('EPWs/DEU_Dusseldorf.104000_IWEC.epw')

    # Alternative 1 to filter without exit
    df_tmy, df_all = weatherObj.typical_day_of_month()

# #
if __name__ == '__main__':
    for month in range(1, 13):
        day = (int(df_all['day_nearest_to_mean'].loc[month]))
        for hour in range(0, 24, 2):
            SimSettings.sim_date_time = f'{month}-{day}_{hour}h'
            if df_tmy['GHI'].loc[month, day, hour] > 50:
                SimSettings.sim_name = (
                    f'APV_Morschenich_{APV_SystSettings.module_form} \
                    _res_{SimSettings.spatial_resolution}\
                        {SimSettings.sim_date_time}')
                brObj = apv.br_wrapper.BR_Wrapper(
                    SimSettings=SimSettings,
                    APV_SystSettings=APV_SystSettings,
                    # weather_file=weather_file,
                )
                evalObj = apv.utils.APV_evaluation.Evaluate_APV(
                    SimSettings=SimSettings,
                    APV_SystSettings=APV_SystSettings
                )
                brObj.setup_br()
                brObj.run_raytracing_simulation()
                brObj.plot_ground_insolation()
                brObj.plot_ground_insolation()

    # #
    evalObj.evaluate_APV()
