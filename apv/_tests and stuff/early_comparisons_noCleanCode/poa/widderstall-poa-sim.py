# #
import importlib as imp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pvlib import irradiance

import holoviews as hv
from holoviews import opts
from bokeh.models import HoverTool
from bokeh.plotting import show

import apv.tools.time
import apv.tools.plots
import apv.tools.evaluation
import apv.resources.locations
import apv.tools.files_interface as fi

imp.reload(apv.tools.time)
imp.reload(apv.tools.evaluation)
imp.reload(apv.resources.locations)
imp.reload(apv.tools.plots)
imp.reload(fi)

df_ws = fi.df_from_file(
    'raw-data/sanyo', skiprows=9, append_all_in_folder=True, delimiter='\t')

# #


def sim_poa(df, timezone):
    df = apv.tools.time.column_to_utc_index(
        df, 'Datum', timezone)

    # POA sim
    site = apv.resources.locations.Widderstall

    # Get solar azimuth and zenith to pass to the transposition function
    solar_position = site.get_solarposition(times=df.index)

    DNI = (df['GHI'] - df['DHI']) / np.cos(
        solar_position['apparent_zenith']*np.pi/180)

    df_POA_irradiance = irradiance.get_total_irradiance(
        surface_tilt=40,    # from widderstall description file
        surface_azimuth=180,  # "
        dni=DNI,
        ghi=df['GHI'],
        dhi=df['DHI'],
        solar_zenith=solar_position['apparent_zenith'],
        solar_azimuth=solar_position['azimuth'],
        # model='klucher'
    )

    df['POA_sim'] = df_POA_irradiance['poa_global']

    return df


def sim_and_plot_poa_for_different_tz(df_ws, timezones: list, xy_max=1200):

    apv.tools.plots.plotStyle(
        fig_width_in_mm=220, width_to_height_ratio=1, marker_size_in_pt=1)

    f, axs = plt.subplots(2, 2, sharex=True, sharey=True)

    for timezone, ax in zip(timezones, axs.ravel()):
        df_ws = sim_poa(df_ws, timezone)

        ax.plot(df_ws['POA'], df_ws['POA_sim'], '+', alpha=0.02)

        # RMSE and MBE
        mbe, rel_mbe, rmse, rel_rmse = apv.tools.evaluation.calc_RMSE_MBE(
            df_ws['POA'], df_ws['POA_sim'])

        ax.plot(
            (0 + mbe*2**0.5, xy_max),
            (0, xy_max - mbe*2**0.5),
            color='k', linewidth=0.3)

        ax.fill_between(
            [0, xy_max],
            [0 - (mbe - rmse)*2**0.5, xy_max - (mbe - rmse)*2**0.5],
            [0 - (mbe + rmse)*2**0.5, xy_max - (mbe + rmse)*2**0.5],
            color='k', alpha=0.2)

        ax.plot((0, xy_max), (0, xy_max), color='r', linewidth=0.3)

        if len(timezones) > 1:
            title = timezone + ', '
        else:
            title = ""
        title = title+'RMSE: ' + \
            '{:.2f}'.format(rmse)+', MBE: '+'{:.2f}'.format(mbe)
        ax.set_title(title)

        ax.set_xlabel('experiment')
        ax.set_ylabel('simulation')
        ax.set_xlim(0, xy_max)
        ax.set_ylim(0, xy_max)
        ax.grid()

    fi.save_fig(
        f, file_name='Widderstall_poa_sim', rel_path='results', dpi=500)


# #
sim_and_plot_poa_for_different_tz(
    df_ws, timezones=['Etc/GMT-2',
                      'Etc/GMT-1',
                      'UTC', 'Etc/GMT+1'
                      ])

# #


def holo_view_poa(df, z, xy_max=1200):

    df['hour'] = df.index.hour

    # setting bokeh as backend
    hv.extension('bokeh')

    compare_plot = hv.Scatter(
        df,  # [500:25000],
        kdims=['POA'],
        vdims=['POA_sim'] + df_ws_gmt_m1.columns.to_list()
    )

    tooltips = [
        (col_name, '@'+col_name) for col_name in df.columns
    ]

    compare_plot.opts(
        show_grid=True, width=600, height=500,
        alpha=0.2, tools=[HoverTool(tooltips=tooltips)],
        xlim=(0, xy_max), ylim=(0, xy_max),
        color=z, cmap='fire', colorbar=True,
        colorbar_opts={'title': z}
    )
    return compare_plot


holo_view_poa(df_ws_gmt_m1, 'GHI')

# #
holo_view_poa(df_ws_gmt_m1, 'hour')

# #
holo_view_poa(df_ws_gmt_m1, 'DHI')
# #
holo_view_poa(df_ws_gmt_m1, 'TAA')
# #
holo_view_poa(df_ws_gmt_m1, 'VW')
# #
df_ws_gmt_m1.columns.to_list()
