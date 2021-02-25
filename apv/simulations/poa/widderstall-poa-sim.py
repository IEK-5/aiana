# #
import importlib as imp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pvlib import irradiance

import holoviews as hv
from holoviews import opts
from holoviews.streams import RangeXY
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

module_ws = fi.df_from_file(
    'raw-data/Sanyo240_moduleSpecs_guestimate.txt', delimiter='\t').T

df_ws = fi.df_from_file(
    'raw-data/sanyo', skiprows=9, append_all_in_folder=True, delimiter='\t')

""" df_ws = apv.tools.time.column_to_utc_index(
    df_ws, timestamp_column_header='Datum', timezone='Etc/GMT-1')
df_ws """

# #


def sim_and_plot_poa_for_different_tz(df_ws, timezones: list, xy_max=1200):
    apv.tools.plots.plotStyle(
        fig_width_in_mm=220, width_to_height_ratio=1, marker_size_in_pt=1)

    f, axs = plt.subplots(2, 2, sharex=True, sharey=True)

    for timezone, ax in zip(timezones, axs.ravel()):
        df_ws = apv.tools.time.column_to_utc_index(
            df_ws, 'Datum', timezone)

        # POA sim
        site = apv.resources.locations.Widderstall

        # Get solar azimuth and zenith to pass to the transposition function
        solar_position = site.get_solarposition(times=df_ws.index)

        DNI = (df_ws['GHI'] - df_ws['DHI']) / np.cos(
            solar_position['apparent_zenith']*np.pi/180)

        POA_irradiance = irradiance.get_total_irradiance(
                surface_tilt=40,  # from widderstall description file
                surface_azimuth=0,
                dni=DNI,
                ghi=df_ws['GHI'],
                dhi=df_ws['DHI'],
                solar_zenith=solar_position['apparent_zenith'],
                solar_azimuth=solar_position['azimuth'])

        df_ws['poa_sim'] = POA_irradiance['poa_global']

        ax.plot(df_ws['POA'], df_ws['poa_sim'], '+', alpha=0.2)

        #######
        # RMSE and MBE
        df_meta = apv.tools.evaluation.calc_RMSE_MBE(
            df_ws['POA'], df_ws['poa_sim'])

        mbe = df_meta.loc['MBE'][0]
        rmse = df_meta.loc['RMSE'][0]

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

        ax.set_xlabel('exp')
        ax.set_ylabel('sim')
        ax.set_title(timezone + ', RMSE: ' + '{:.2f}'.format(rmse))
        ax.set_xlim(0, xy_max)
        ax.set_ylim(0, xy_max)
        ax.grid()

    fi.save_fig(
        f, file_name='Widderstall_poa_sim', rel_path='results', dpi=500)

    return df_meta

sim_and_plot_poa_for_different_tz(
    df_ws, timezones=['Etc/GMT-2', 'Etc/GMT-1', 'UTC', 'Etc/GMT+1'])


# #
# setting bokeh as backend
hv.extension('bokeh')

compare_plot = hv.Scatter(df_ws, ['POA', 'poa_sim'])

tooltips = [
    ('Time', '@Datum'),
    ('POA', '@POA'),
    ('poa_sim', '@poa_sim')
]
hover = HoverTool(tooltips=tooltips)

# Apply options
compare_plot.opts(
    opts.Scatter(
        framewise=True, show_grid=True, width=600, height=500,
        alpha=0.2, xlim=(0, 1600), ylim=(0, 1600), tools=[hover]),
    opts.Image(
        cmap='fire', logz=True, height=800, width=800, xaxis=None, yaxis=None))
""" dmap.opts(
    opts.Histogram(framewise=True, logy=True, width=200, xlim=(1, None)),
    opts.Image(cmap='fire', logz=True, height=600, width=600,
               xaxis=None, yaxis=None)) """


# use show() from bokeh
show(hv.render(compare_plot))
# #
