# #
import importlib as imp
import pandas as pd
import matplotlib.pyplot as plt

import apv.tools.time
import apv.tools.plots
import apv.tools.evaluation
import apv.tools.files_interface as fi

imp.reload(apv.tools.time)
imp.reload(apv.tools.evaluation)
imp.reload(apv.tools.plots)
imp.reload(fi)

'''
the "ads" data is satelite based and from
https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-solar-radiation-timeseries?tab=form
the "ws" data is from a ground station in Widderstall and from Barts file
'''
# #
df_ws = fi.df_from_file(
    'raw-data/sanyo', skiprows=9, append_all_in_folder=True, delimiter='\t')
df_ws = apv.tools.time.column_to_utc_index(df_ws, 'Datum', 'Etc/GMT-1')
df_ws

# #
df_ads = fi.df_from_file(
    'raw-data/ads', skiprows=42, delimiter=';', append_all_in_folder=True)

# #


def add_timestampIndex_equal_to_start_of_observation_period(
        df: pd.DataFrame,
        observation_period_header='Observation period'
        ) -> pd.DataFrame:

    df_start_end = df[observation_period_header].str.split('/', expand=True)
    # set observation-start as index
    df = df.set_index(pd.to_datetime(df_start_end[0]))
    df.index = df.index.tz_localize('UTC')
    df.index.names = ['time_utc']

    return df


def average_var_to_timestamp_between_observation_periods(
        df: pd.DataFrame, variables: list) -> pd.DataFrame:

    '''
    to eleminate around 4% deviations
    '''

    for variable in variables:
        # calculating an instantaneous value around the index-timestamp by
        # taking the average of the value for the previous period and the
        # current period
        df[variable] = ((df[variable]+df[variable].shift(1))/2)

    return df


# prepare data
df_ws = apv.tools.time.add_missing_timestamp_indices(df_ws)
df_ads = add_timestampIndex_equal_to_start_of_observation_period(df_ads)
df_ads = apv.tools.time.add_missing_timestamp_indices(df_ads)
variables = ['GHI', 'DHI']
df_ads = average_var_to_timestamp_between_observation_periods(
    df_ads, variables)

# #
df_ads
# #
# slice to 5 mins
df_ads2 = df_ads.iloc[::5].copy()
# one hour shift needed to take time zone differences into account
# df_ads2.index = df_ads2.index.shift(24)


def verify_synchronity(
        y1: pd.Series, y2: pd.Series,
        i_start=0, i_end=1200):

    y1[i_start:i_end].plot()
    y2[i_start:i_end].plot()

verify_synchronity(df_ads2['GHI']*60, df_ws['GHI'])



# #
# merge to match times
df_merged = pd.merge(
    df_ws[variables],
    df_ads2[variables]*60,  # *60 to convert from W*hrs to W
                            # (1hr/1min = 3600s/60s)
    left_index=True, right_index=True)


def plot_comparison(variables: list, xy_max=1000):
    f, axs = plt.subplots(1, 2, sharey=True)

    apv.tools.plots.plotStyle(
        fig_width_in_mm=220, width_to_height_ratio=2.2, marker_size_in_pt=1)

    for variable, ax in zip(variables, axs.ravel()):

        ax.plot(
            df_merged[variable+'_x'], df_merged[variable+'_y'],
            '+', alpha=0.3)
        ax.set_xlabel('Widderstall')
        ax.set_ylabel('ADS')
        ax.set_title('$'+variable+'$ [W/m$^2$]')
        ax.set_xlim(0, xy_max)
        ax.set_ylim(0, xy_max)
        ax.grid()
        ax.plot((0, xy_max), (0, xy_max), c='r', linewidth=0.3)

    fi.save_fig(
        f, file_name='Widderstall_vs_ads_'+str(variables),
        rel_path='results', dpi=500)


plot_comparison(variables)

# #
plot_comparison(variables, xy_max=400)

# #

df_meta = apv.tools.evaluation.calc_RMSE_MBE(df_ws['GHI'], df_ads2['GHI'])
df_meta

# #
df_meta = apv.tools.evaluation.calc_RMSE_MBE(df_ws['DHI'], df_ads2['DHI'])
df_meta

