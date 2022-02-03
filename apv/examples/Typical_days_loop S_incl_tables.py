# #
# 1. max
# 2. ost mean
# 3. north mean,
# 4. south mean
# #
"""dont do test code outside of if __name__=='__main__'
or it will make problems with multi processing
"""
if __name__ == '__main__':
    from apv.utils import files_interface
    import pytictoc
    from pathlib import Path
    import importlib as imp
    import apv
    import os
    from typing import Literal
    from apv.classes.sim_datetime import SimDT
    from apv.classes.geometries_handler import GeometriesHandler
    import apv.utils.files_interface as fi

    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.br_wrapper)

    # ############ SIM SETTINGS #############
    SimSettings = apv.settings.simulation.Simulation()
    # SimSettings.sim_name = 'APV_Morschenich_S_inclinedTables'

    position: Literal['north', 'center', 'south', 'east'] = 'center'
    plots_shifts_xy = {'north': [0, 1], 'center': [0, 0],
                       'south': [0, -1], 'east': [3, 0]}

    SimSettings.sim_name = f'APV_Morschenich_S_inclinedTables'

    SimSettings.use_typDay_perMonth_for_shadowDepthCalculation = True
    SimSettings.spatial_resolution = 0.1
    SimSettings.time_step_in_minutes = 5  # 6
    # SimSettings.use_multi_processing = False
    SimSettings.sim_date_time = '06-15_7:00'
    SimSettings.TMY_irradiance_aggfunc = 'mean'
    # only for view_scene, will be overwritten by for loops
    #########################################

    # ### APV_SystSettings:  ####
    APV_SystSettings = \
        apv.settings.apv_systems.APV_Syst_InclinedTables_S_Morschenich()
    # APV_SystSettings = apv.settings.apv_systems.APV_Morchenich_EastWest()
    # APV_SystSettings.module_form = 'none'

    # ================== comment this out fo real simulation ==================
    # APV_SystSettings.add_groundScanArea_as_object_to_scene = True
    # ================== =============== ================== ===============

    APV_SystSettings.add_airrails = True
    x_reduction = -((APV_SystSettings.moduleDict['x']
                     + APV_SystSettings.moduleDict['xgap'])
                    * (APV_SystSettings.sceneDict['nMods']))/2+2  # =2*2m=4m
    y_reduction = (-APV_SystSettings.sceneDict['pitch']
                   - APV_SystSettings.moduleDict['y']/2)
    APV_SystSettings.ground_scan_margin_x = x_reduction  # -3
    APV_SystSettings.ground_scan_margin_y = y_reduction  # -32
    APV_SystSettings.ground_scan_shift_x = 2 + plots_shifts_xy[position][0]*4  # -32
    APV_SystSettings.ground_scan_shift_y = \
        APV_SystSettings.sceneDict['pitch'] * plots_shifts_xy[position][1]\
        + APV_SystSettings.mountingStructureDict['inner_table_post_distance_y']

    # #
    brObj = apv.br_wrapper.BR_Wrapper(SimSettings, APV_SystSettings,
                                      # debug_mode=True
                                      )
    brObj.setup_br()

    # #
    brObj.view_scene(view_name='top_down', view_type='parallel'
                     )
# #
if __name__ == '__main__':
    ###########################################################################
    setup_br_and_simulate = True
    ###########################################################################
    months = [6]
    # months = range(1, 13)
    # hours = [19]
    hours = range(19, 24, 1)
    # minutes = [10]
    minutes = range(0, 60, SimSettings.time_step_in_minutes)
    # minute 60 is and has to be exclusive

    sun_shines = False  # (for ghi filter (no relation to cloudy days))

    for month in months:
        day = 15  # (int(df_all['day_nearest_to_mean'].loc[month]))

        df_tdm = brObj.weatherData.df_irradiance_typ_day_per_month
        cumulative_GHI = df_tdm.loc[(month), 'ghi_Whm-2'].sum()

        brObj.results_subfolder = files_interface.create_results_folder_path(
            SimSettings, APV_SystSettings
        ) / f'month-{month}_{position}-position'

        for hour in hours:
            geomObj = GeometriesHandler(APV_SystSettings)
            # TODO syst cloning should be called also in geometries handler
            # and not in br_wrapper

            for minute in minutes:
                # to measure elapsed time:
                tictoc = pytictoc.TicToc()
                tictoc.tic()
                # set time with leading zeros for a correct file order
                SimSettings.sim_date_time = \
                    f'{month:02}-{day}_{hour:02}:{minute:02}'
                simDT = SimDT(SimSettings)

                # set sunpos
                brObj.weatherData.set_dhi_dni_ghi_and_sunpos_to_simDT(simDT)

                # get ghi, dhi, dni
                hour_utc = simDT.sim_dt_utc.hour
                ghi = df_tdm.loc[(month, hour_utc, minute), 'ghi_Wm-2']
                dhi = df_tdm.loc[(month, hour_utc, minute), 'dhi_Wm-2']
                dni = ghi-dhi  # (as ground has tilt 0)

                if (brObj.weatherData.sunalt < 0):
                    print(f'Sun alitude < 0 ({brObj.weatherData.sunalt}).')
                # elif (ghi < cumulative_GHI * 0.02) or (ghi > 50):
                elif ghi < min(cumulative_GHI * 0.02, 50):

                    print(f'GHI too low ({ghi} Wh/m²).')
                    if sun_shines is True:
                        SimSettings.enddt = SimSettings.sim_date_time
                        sun_shines = False
                else:
                    if sun_shines is False:
                        SimSettings.startdt = SimSettings.sim_date_time
                        sun_shines = True

                    brObj.SimSettings = SimSettings
                    if setup_br_and_simulate:
                        brObj.setup_br(
                            dni_singleValue=dni, dhi_singleValue=dhi)
                        # brObj.view_scene(
                        #    view_name='top_down', view_type='parallel')
                        ########
                        brObj.run_raytracing_simulation()
                        ########
                        for cm_unit in ['radiation', 'shadow_depth']:
                            brObj.plot_ground_heatmap(cm_unit=cm_unit)
                tictoc.toc()

# #
# ======================================================
# cumulate
# ======================================================

# #
if __name__ == '__main__':
    months = [6]
    month = 6
    for agg_func in ['min', 'mean', 'max']:  # ['min', 'mean', 'max']:  # month in months:

        SimSettings.TMY_irradiance_aggfunc = agg_func
        brObj = apv.br_wrapper.BR_Wrapper(SimSettings, APV_SystSettings,
                                          # debug_mode=True
                                          )
        brObj.setup_br()

        enddts = {
            'min': '6-15_20:00', 'mean': '6-15_20:50', 'max': '6-15_21:00'}

        brObj.results_subfolder = files_interface.create_results_folder_path(
            SimSettings, APV_SystSettings
        ) / f'month-{month}_{position}-position'

        def get_date_time_str(file_name: str) -> str:
            string_parts = file_name[:-4].replace('h', ':').split('_')
            return f'{string_parts[2]}_{string_parts[3]}'

        def set_startdt_and_enddt_based_on_files(folder_path: Path):
            """for plot title"""
            file_list = os.listdir(str(folder_path))
            brObj.SimSettings.startdt = get_date_time_str(file_list[0])
            # TODO add zero to single digit hours in file name
            # get_date_time_str(file_list[-1]) + time_step_in_minutes...
            brObj.SimSettings.enddt = enddts[agg_func]

        set_startdt_and_enddt_based_on_files(brObj.results_subfolder / 'data')

        ###########################################################################
        appended_data = []

        results_subfolder_cum = brObj.results_subfolder / 'cumulative'

        apv.utils.files_interface.make_dirs_if_not_there(results_subfolder_cum)
        cum_file_name = 'ground_results' + '_cumulative_' + str(month)
        cum_csv_path = results_subfolder_cum / Path(cum_file_name + '.csv')

        # TODO was muss wirklich neu gesetzt werden?
        # oder arbeiten wir lieber mit zwangsübergabe ohne default settings?
        # brObj.evalObj.SimSettings = SimSettings  # wahrscheinlich unnötig

        #
        if cum_csv_path.exists():  # and not debug_mode...
            df_merged = apv.utils.files_interface.df_from_file_or_folder(
                cum_csv_path)
        else:  # cummulate:
            # testing same times for ghi clear sky cum
            SimSettings.startdt = '6-15_06:15'  # TODO why does this have no effect?!
            SimSettings.enddt = '6-15_21:00'
            df_merged = brObj.evalObj.cumulate_gendaylit_results(
                brObj.results_subfolder / Path('data'),
                cum_csv_path, SimSettings
            )

        # min, max for equal color maps
        csv_files = []
        for agg_func2 in ['min', 'mean', 'max']:
            csv_files += [str(cum_csv_path).replace(
                f'aggfunc-{agg_func}', f'aggfunc-{agg_func2}')]
        df_limits = fi.get_min_max_of_cols_in_several_csv_files(
            csv_files).round(1)

        # plot
        for cm_unit in ['shadow_depth',
                        'radiation', 'DLI'
                        ]:
            brObj.plot_ground_heatmap(
                df_merged, file_name=cum_file_name,
                destination_folder=results_subfolder_cum,
                cumulative=True,
                cm_unit=cm_unit
            )

            brObj.plot_ground_heatmap(
                df_merged, file_name=cum_file_name+'_equalColLimits',
                destination_folder=results_subfolder_cum,
                cumulative=True,
                cm_unit=cm_unit,
                df_col_limits=df_limits
            )

# #
