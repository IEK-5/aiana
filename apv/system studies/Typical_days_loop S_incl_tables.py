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
    import pytictoc
    from pathlib import Path
    import importlib as imp
    import apv
    import os
    from typing import Literal
    from apv.classes.util_classes.sim_datetime import SimDT
    from apv.classes.geometries_handler import GeometriesHandler
    import apv.utils.files_interface as fi

    imp.reload(apv.classes.geometries_handler)
    imp.reload(apv.settings.apv_systems)
    imp.reload(apv.classes.br_wrapper)

    # ############ SIM SETTINGS #############
    SimSettings = apv.settings.simulation.Simulation()
    # SimSettings.sim_name = 'APV_Morschenich_S_inclinedTables'
    SimSettings.sim_name = f'APV_Morschenich_S_inclinedTables'
    SimSettings.position = 'south'

    SimSettings.use_typDay_perMonth_for_shadowDepthCalculation = True
    SimSettings.spatial_resolution = 0.1
    SimSettings.time_step_in_minutes = 5  # 6
    # SimSettings.use_multi_processing = False
    SimSettings.sim_date_time = '06-15_12:00'
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

    # APV_SystSettings.add_airrails = False
    x_reduction = -((APV_SystSettings.moduleDict['x']
                     + APV_SystSettings.moduleDict['xgap'])
                    * (APV_SystSettings.sceneDict['nMods']))/2+2  # =2*2m=4m
    y_reduction = (-APV_SystSettings.sceneDict['pitch']
                   - APV_SystSettings.moduleDict['y']/2)
    APV_SystSettings.ground_scan_margin_x = x_reduction  # -3
    APV_SystSettings.ground_scan_margin_y = y_reduction  # -32
    # -32
    APV_SystSettings.ground_scan_shift_x = 2 + \
        SimSettings.plots_shifts_xy[SimSettings.position][0]*4
    APV_SystSettings.ground_scan_shift_y = \
        APV_SystSettings.sceneDict['pitch'] \
        * SimSettings.plots_shifts_xy[SimSettings.position][1]\
        + APV_SystSettings.mountingStructureDict['inner_table_post_distance_y']

    def modify_results_subfolder(SimSettings, APV_SystSettings, month, posi):
        return fi.create_results_folder_path(
            SimSettings, APV_SystSettings) / f'month-{month}_{posi}-position'
    # #
    brObj = apv.classes.br_wrapper.BR_Wrapper(SimSettings, APV_SystSettings,
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
    hours = range(17, 24, 1)
    # minutes = [10]
    minutes = range(0, 60, SimSettings.time_step_in_minutes)
    # minute 60 is and has to be exclusive

    sun_shines = False  # (for ghi filter (no relation to cloudy days))

    for month in months:
        day = 15  # (int(df_all['day_nearest_to_mean'].loc[month]))

        df_tdm = brObj.weatherData.df_irradiance_typ_day_per_month
        cumulative_GHI = df_tdm.loc[(month), 'ghi_Whm-2'].sum()

        brObj.results_subfolder = modify_results_subfolder(
            SimSettings, APV_SystSettings, month, SimSettings.position)

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
    def meta_cumulate(agg_funcs: list, positions: list, equalColLims=False):
        month = 6
        for agg_func in agg_funcs:
            for position in positions:
                SimSettings.position = position
                SimSettings.TMY_irradiance_aggfunc = agg_func
                brObj = apv.classes.br_wrapper.BR_Wrapper(SimSettings, APV_SystSettings,
                                                          # debug_mode=True
                                                          )
                # brObj.setup_br()
                brObj.results_subfolder = modify_results_subfolder(
                    SimSettings, APV_SystSettings, month, SimSettings.position)

                def get_date_time_str(file_name: str) -> str:
                    string_parts = file_name[:-4].replace('h', ':').split('_')
                    return f'{string_parts[2]}_{string_parts[3]}'

                def set_startdt_and_enddt_based_on_files(folder_path: Path):
                    """for plot title"""
                    file_list = os.listdir(str(folder_path))
                    brObj.SimSettings.startdt = get_date_time_str(file_list[0])
                    # TODO add zero to single digit hours in file name
                    # get_date_time_str(file_list[-1]) + time_step_in_minutes...
                    enddts = {'min': '6-15_20:00', 'mean': '6-15_20:50',
                              'max': '6-15_21:00'}
                    brObj.SimSettings.enddt = enddts[agg_func]

                set_startdt_and_enddt_based_on_files(brObj.results_subfolder / 'data')

                ###########################################################################
                results_subfolder_cum = brObj.results_subfolder.parent.parent\
                    / 'cumulative'
                fi.make_dirs_if_not_there(results_subfolder_cum)
                cum_file_name = brObj.return_plot_title(
                    title_comps=['weather', 'position'],
                    cumulative=True)  # +' - month '+str(month)
                cum_file_name = cum_file_name.replace('\n', ' - ').replace(':', '')
                cum_csv_path = results_subfolder_cum / f'{cum_file_name}.csv'

                # TODO was muss wirklich neu gesetzt werden?
                # oder arbeiten wir lieber mit zwangsübergabe ohne default settings?
                # brObj.evalObj.SimSettings = SimSettings  # wahrscheinlich unnötig

                #
                if cum_csv_path.exists():  # and not debug_mode...
                    df_merged = fi.df_from_file_or_folder(
                        cum_csv_path)
                else:  # cummulate:
                    # testing same times for ghi clear sky cum
                    SimSettings.startdt = '6-15_06:15'  # TODO why does this have no effect?!
                    SimSettings.enddt = '6-15_21:00'
                    df_merged = brObj.evalObj.cumulate_gendaylit_results(
                        brObj.results_subfolder / Path('data'),
                        cum_csv_path, SimSettings
                    )

                # gather file pathes to get min, max  for equal color maps
                csv_files = []
                if len(agg_funcs) > 1:
                    heatmap_subfolder = f'weather-variation position-{position}'
                    for weather in ['clear sky', 'mean cloudy', 'max cloady']:
                        csv_files += [str(cum_csv_path).replace(
                            brObj.return_weather_description(), weather)]

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
                    brObj.plot_ground_heatmap(
                        df_merged, file_name=cum_file_name+'',
                        destination_folder=results_subfolder_cum/Path(
                            f'{heatmap_subfolder}{folder_extension}'),
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