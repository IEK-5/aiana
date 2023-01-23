""" This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>."""

# #
from matplotlib import pyplot as plt
import seaborn as sn
import numpy as np
from aiana.utils import files_interface as fi
import os
import pandas as pd
from aiana.classes.aiana_main import AianaMain
from aiana.classes.util_classes.settings_handler import Settings
from aiana.settings.apv_system_settings import APV_Syst_InclinedTables_S_Morschenich
from aiana.utils.study_utils import adjust_settings_StudyForMorschenich

if __name__ == '__main__':
    settings = Settings()
    settings.apv = APV_Syst_InclinedTables_S_Morschenich()
    settings.sim.study_name = 'APV_Morschenich_2022_IGB2'

    start_month = 1  # or 3
    start_day = 6  # or 31, Thursdays

    settings.sim.month = start_month
    settings.sim.day = start_day

    settings.sim.hours = list(range(12, 13))
    settings.sim.hours = list(range(4, 23))
    settings = adjust_settings_StudyForMorschenich(settings)
    # settings.apv.module_form = 'none' #useful tp align the groundScanArea
    am = AianaMain(settings)
    # am.create_and_view_octfile_for_SceneInspection(
    #     # view_name='top_down',
    #     add_NorthArrow=False, add_sensor_vis=False, add_groundScanArea=False
    # )
    end_KW = 33

# #
# exp start = thuesday 19.4. (KW 16), but did now from KW1
# exp end = 12.8. (KW 32)
# doing simulations at Thursdays as requested
if __name__ == '__main__':
    start_KW = 1
    finished_KW = 0  # enter last successfully simulated KW, if sim was aborted
    for week_shift in (i for i in range(finished_KW-start_KW+1, end_KW-start_KW+1)):
        am.update_simTime_and_resultPaths(
            month=start_month, day=start_day)  # reset
        current_timestamp = pd.to_datetime(am.settings._dt.sim_dt_utc) \
            + pd.Timedelta(f'{7*week_shift}day')
        day = current_timestamp.day
        month = current_timestamp.month
        am.update_simTime_and_resultPaths(month=month, day=day)
        KW = am.settings._dt.week
        am.settings.sim.sub_study_name = f'KW{str(KW).zfill(2)}'
        print(day, month, f'KW: {KW}, week_shift: {week_shift}')
        am.simulate_and_evaluate(skip_sim_for_existing_results=True,
                                 tasks=['sim']  # skipping time_step_plots
                                 )


# #
# evaluation
if __name__ == '__main__':
    def add_p_col_p_row_and_below_columns(df: pd.DataFrame) -> pd.DataFrame:
        # match result slices to the experimental harvest areas
        pitch = am.settings.apv.sceneDict['pitch']  # 7.32 m
        edge_distance = 1
        # number of plots in x,y:
        nx, ny = 8, 3
        # length of plots in x,y:
        lx, ly = 1.2, 1.2
        harvest_plot_distance_within_same_p_row = pitch-2*(ly+edge_distance)
        # (= 2.92 m)

        df_minmax = df.agg([min, max])
        l_y_all = df_minmax.at['max', 'y']-df_minmax.at['min', 'y']

        # start coordinate of harvest plots in x, y:
        sx, sy = df_minmax.at['min', 'x'], df_minmax.at['min', 'y']
        sy_mod = sy+edge_distance
        sy_open = sy_mod + harvest_plot_distance_within_same_p_row+ly

        cols = list(range(1, nx+1))
        rows = list(range(1, ny+1))

        conditions = [((df['x'] >= sx+(cols-1)*lx)
                       & (df['x'] < sx+cols*lx)) for cols in cols]
        df['p_col'] = np.select(conditions, cols)
        conditions = [((df['y'] >= sy+(row-1)*pitch)
                       & (df['y'] < sy+row*pitch)) for row in rows]
        df['p_row'] = np.select(conditions, rows)

        # separate harvest zones into the two categories:
        # below modules | open beams
        def set_below_what(
                df: pd.DataFrame, below_what: str, y_start: float) -> pd.DataFrame:

            conditions = [((df['y'] >= y_start+(row-1)*pitch)
                           & (df['y'] < y_start+ly+(row-1)*pitch)) for row in rows]
            df['below'] = np.select(conditions, [below_what]*3)
            return df

        df = set_below_what(df, below_what='modules', y_start=sy_mod)
        df[df['below'] != 'modules'] = set_below_what(
            # as we do not want to overwrite the modules labels
            df[df['below'] != 'modules'], below_what='open beams', y_start=sy_open)

        for col_name in ['p_col', 'p_row', 'below']:
            print(f'{df[(df[col_name]==0) | (df[col_name]=="0")].shape[0]/df.shape[0]*100:1g} % ',
                  f'set to nan for {col_name} due to sensors beyond filter array.')
            # below a lot is filtered away as only 6x1.2 m stripes are kept
            # from the complete field (y total = 3*7.32 m)
        return df

# cumulative:
if __name__ == '__main__':
    def gather_cumulative_reference_DLI_values() -> dict:
        refDLIs: dict = {}  # [mol/m²]
        for week_shift in (i for i in range(0, end_KW+1)):
            am.update_simTime_and_resultPaths(
                month=start_month, day=start_day)  # reset
            current_timestamp = pd.to_datetime(am.settings._dt.sim_dt_utc) \
                + pd.Timedelta(f'{7*week_shift}day')
            day = current_timestamp.day
            month = current_timestamp.month
            am.update_simTime_and_resultPaths(month=month, day=day)
            am.weatherData.calc_cumulative_ghi()
            KW = am.settings._dt.week

            refDLIs.update({KW: 0.0074034*am.weatherData.dailyCumulated_ghi})
        return refDLIs

# gather_cumulative_reference_DLI_values()

    # #
    # gather sim result folders
    folders = os.listdir(am.settings._paths.cum_csv_file_path.parents[1])

    for _ in range(4):  # why does it not work in one run !?
        for folder in folders:
            if ('.' in folder) or ('KW' not in folder):
                folders.remove(folder)
    folders

    # #
    # gather all daily cumulative results in one dataframe
    def read(folders):
        for folder in folders:
            df = fi.df_from_file_or_folder(
                am.settings._paths.cum_csv_file_path.parents[1]/folder,
                append_all_in_folder=True)
            df['KW'] = int(folder.split('_')[0][2:])
            yield df
    df = pd.concat(read(folders))
    df
    # #

    df = add_p_col_p_row_and_below_columns(df)
    # #
    # set results to NaN which are outside of the exp. harvest area
    # (NOTE simulating a big area at once instead of smaller ones is still much
    # faster with a decent GPU)
    for col_name in ['Whm2', 'PARGround_cum', 'ShadowDepth_cum']:
        df[col_name] = np.where(df['below'] == "0", np.NaN, df[col_name])

    # #
    # filtered heatmaps for each KW, also to check visually
    for KW in df['KW'].unique():
        df_plt_test = df[df['KW'] == KW]
        title = f'Daily cum in KW {KW}'
        am.plotterObj.ground_heatmap(
            df_plt_test, cumulative=True, plot_title=title, plot_dpi=300,
            destination_file_path=am.settings._paths.cum_csv_file_path.parents[1]
            / 'filtered heatmaps'/f'{title}.jpg')

    # #
    # # # additional result plots # # #
    # creating a DLI scatterplot with separated plot rows (p_row)
    # and plot columns (p_col)
    # if group_p_rows_cols = False

    # and creating a weekly cumulative light integral for all KWs,
    # if group_p_rows_cols = True
    def aggregate_cumulative_df_and_plot(
            df: pd.DataFrame, group_p_rows_cols=True) -> pd.DataFrame:
        # group_p_rows_cols = False takes ca a minute
        groupby_list = ['KW', 'below']

        if group_p_rows_cols == False:
            groupby_list += ['p_row', 'p_col']
        df_agg0 = df.groupby(groupby_list, as_index=False).mean()

        del df_agg0['x']
        del df_agg0['y']
        df_agg0 = am.evaluatorObj._add_DLI(df_agg0)
        del df_agg0['PARGround_cum']
        del df_agg0['Whm2']

        if group_p_rows_cols:
            del df_agg0['p_row']
            del df_agg0['p_col']

        df_agg_mods = df_agg0[df_agg0['below'] == 'modules']
        df_agg_open = df_agg0[df_agg0['below'] == 'open beams']
        df_agg_ref = df_agg_open.copy()  # dummy
        df_agg_ref['below'] = 'sky'
        df_agg_ref['ShadowDepth_cum'] = 0

        refDLIs = gather_cumulative_reference_DLI_values()
        conditions = [df_agg_ref['KW'] == key for key in refDLIs.keys()]
        df_agg_ref['DLI'] = np.select(conditions, refDLIs.values())
        if group_p_rows_cols:
            for df_x in [df_agg_mods, df_agg_open, df_agg_ref]:
                df_x.loc[:, 'cum_WLI[mol/m²]'] = df_x.loc[:, 'DLI'].cumsum()*7

        df_agg = pd.concat([df_agg_mods, df_agg_open, df_agg_ref]).reset_index()

        df_agg.rename(columns={'DLI': 'DLI [mol/m²]'}, inplace=True)
        df_agg.rename(columns={'level_0': 'index'}, inplace=True)

        #df_agg.set_index('index', inplace=True)
        df_agg.sort_index(inplace=True)
        # return df_agg
        sn.set_style('darkgrid')
        if group_p_rows_cols == True:
            # cumsum WLI vs KW lineplot
            x = 'KW'
            y = 'cum_WLI[mol/m²]'
            ax = sn.lineplot(data=df_agg, x=x, y=y, hue='below')
            ax.set(xlabel='isocalendar week',
                   ylabel=f'cumulative weekly light integral [mol/m²]',
                   xlim=(1, 33))
            plt.savefig(am.settings._paths.results_folder/f'cum_WLIs.png', dpi=300)

        else:
            # scatter plot per KW, p_row and p_col
            x, y = 'p_col', 'DLI [mol/m²]'
            g = sn.FacetGrid(
                data=df_agg, row='KW', col='p_row', hue='below', margin_titles=True)
            g.map(sn.scatterplot, x, y)
            g.add_legend()

        fi.df_export(df_agg, am.settings._paths.results_folder /
                     f'morschenich_simresults_perKW-2022.csv', sep=';')
        return df_agg

    df_agg = aggregate_cumulative_df_and_plot(df)
    df_agg
    # #
# #
# daily data
# 5.5., 23.6., 11.8.22


def aggregate_daily_df_and_plot(
        df: pd.DataFrame, day, month,
        group_p_rows_cols=True) -> pd.DataFrame:
    # group_p_rows_cols = False takes ca a minute

    groupby_list = ['time_utc', 'below']
    if group_p_rows_cols == False:
        groupby_list += ['p_row', 'p_col']
    df_agg0 = df.groupby(groupby_list, as_index=False).mean()

    del df_agg0['x']
    del df_agg0['y']

    df_agg0['time_utc'] = pd.to_datetime(df_agg0['time_utc'], utc=True)
    df_agg0['DLI_per_timestep'] = df_agg0['Wm2']\
        * am.settings.sim.time_step_in_minutes/60 * 0.0074034
    del df_agg0['PARGround']
    del df_agg0['Wm2']

    if group_p_rows_cols:
        del df_agg0['p_row']
        del df_agg0['p_col']

    df_agg_mods = df_agg0[df_agg0['below'] == 'modules']
    df_agg_open = df_agg0[df_agg0['below'] == 'open beams']
    df_agg_ref = df_agg_open.copy()  # dummy
    df_agg_ref['below'] = 'sky'

    df_agg_ref['ShadowDepth'] = 0
    df_agg_ref['time_utc']

    ref_ghi: pd.Series = am.weatherData.df_irradiance_typical_day['ghi_Whm-2']
    # conditions = [df_agg_ref['time_utc'] == ref_ghi.index]
    for dtime in df_agg_ref['time_utc']:  # not so performant but works
        df_agg_ref.loc[df_agg_ref['time_utc'] == dtime, 'DLI_per_timestep'] = \
            ref_ghi.loc[(KW, dtime.hour, dtime.minute)] * 0.0074034
    for df_x in [df_agg_mods, df_agg_open, df_agg_ref]:
        df_x.loc[:, 'DLI'] = df_x['DLI_per_timestep'].cumsum()

    df_agg = pd.concat([df_agg_mods, df_agg_open, df_agg_ref]).reset_index()

    df_agg.rename(columns={'DLI': 'DLI [mol/m²]'}, inplace=True)

    del df_agg['level_0']
    del df_agg['index']

    #df_agg.set_index('index', inplace=True)
    df_agg.sort_index(inplace=True)
    # return df_agg
    sn.set_style('darkgrid')
    if group_p_rows_cols == True:

        for suffix in ['', '_per_timestep']:

            x = 'time_utc'
            if suffix == '':
                y = f'DLI [mol/m²]'
            else:
                y = f'DLI{suffix}'

            filename = f'DLI{suffix}_{day}-{month}-2022'
            fig, ax = plt.subplots(1, 1)
            ax = sn.lineplot(data=df_agg, x=x, y=y, hue='below')
            ax.set(xlabel='month-day hour',
                   ylabel=f'daily light integral{suffix} [mol/m²]',
                   #xlim=(1, 33)
                   )
            fig.savefig(am.settings._paths.results_folder/f'{filename}.png', dpi=300)
    else:  # TODO untested
        # scatter plot per KW, p_row and p_col
        x, y = 'p_col', 'DLI [mol/m²]'
        g = sn.FacetGrid(
            data=df_agg, row='KW', col='p_row', hue='below', margin_titles=True)
        g.map(sn.scatterplot, x, y)
        g.add_legend()

    fi.df_export(df_agg, am.settings._paths.results_folder /
                 f'morschenich_simresults_{day}-{month}-2022.csv', sep=';')
    return df_agg


for (day, month, KW) in [(5, 5, 18),
                         (23, 6, 25),
                         (11, 8, 32)
                         ]:
    folder_path = rf'D:\aiana_simulation_results\APV_Morschenich_2022_IGB2\KW{str(KW).zfill(2)}_std-module_2022-{str(month).zfill(2)}-{str(day).zfill(2)}_data\instantaneous_csv_files'
    df = fi.df_from_file_or_folder(folder_path, append_all_in_folder=True)
    del df['Unnamed: 0']
    del df['z']
    del df['mattype']
    df = add_p_col_p_row_and_below_columns(df)

    # set results to NaN which are outside of the exp. harvest area
    for col_name in ['Wm2', 'PARGround', 'ShadowDepth']:
        df[col_name] = np.where(df['below'] == "0", np.NaN, df[col_name])

    df_agg = aggregate_cumulative_df_and_plot(df, day, month, cumulative=False)

df_agg


for time_utc in df['time_utc'].unique():
    df_plt_test = df[df['time_utc'] == time_utc]
    title = f'GGI at time_utc {str(time_utc[:-9]).replace(":","h")}'
    am.plotterObj.ground_heatmap(
        df_plt_test, plot_title=title, plot_dpi=300,
        destination_file_path=am.settings._paths.cum_csv_file_path.parents[1]
        / 'filtered heatmaps/GGI'/f'{title}.jpg')
