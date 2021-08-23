import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import holoviews as hv
from bokeh.models import HoverTool
from holoviews.streams import RangeXY

import pandas as pd
from scipy import stats
import seaborn as sns

import apv
from apv.settings import APV_System as APV_SystSettings


def plot_heatmap(
        df: pd.DataFrame,
        x: str,
        y: str,
        z: str,
        x_label=None,
        y_label=None,
        z_label=None,
        plot_title='',
        cm='inferno',
        ticklabels_skip_count_number="auto"
) -> Figure:
    """Creates a Figure containing a seaborn heatmap
    (side note, relevant for adding drawings: its colored square patches
     are string-labeled and have always matplotlib coordinates-based
     edge-lengths equal to 1)

    Args:
        df (pd.DataFrame): dataframe containing the input data
        x, y, z (str): header of the df column, whose data is to be used
        for the x-axis, y-axis, or color-map, respectivly.
        x_label, y_label, z_label (str, optional): label overwrites.
        Defaults to None, which results in label = x, y, or z, respectivly.
        cm (str, optional): color map style. Defaults to 'inferno'.

    Returns:
        Figure: matplotlib.figure.Figure object, which can be modified
        or saved later.
    """

    # prepare and print heatmap-input data for inspection
    data = df.pivot(y, x, z)
    print(data)

    # create a figure object, which is a top level container for subplots
    # and axes objects, which are the subplots (here only one)
    fig, ax = plt.subplots(1, 1  # , figsize=(8, 4)
                           )
    # plot title
    ax.set_title(plot_title)

    # axis label overwrites
    if x_label is None:
        x_label = x
    if y_label is None:
        y_label = y
    if z_label is None:
        z_label = z

    sns.heatmap(
        data,
        annot=False,
        linewidths=0,
        ax=ax,  # only relevant for later if there are more than one ax
        square=True,
        xticklabels=ticklabels_skip_count_number,
        yticklabels=ticklabels_skip_count_number,
        cmap=cm,
        cbar_kws={'label': z_label}
    )
    # To resemble Radiance coordinates
    ax.invert_yaxis()

    # overwrites x and y labels given by seaborn
    ax.tick_params()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    # x,y tick labels format and rotation
    xlabels = ['{:.2g}'.format(float(item.get_text()))
               for item in ax.get_xticklabels()]
    ylabels = ['{:.2g}'.format(float(item.get_text()))
               for item in ax.get_yticklabels()]
    ax.set_xticklabels(xlabels, rotation=0)
    ax.set_yticklabels(ylabels, rotation=0)

    # add_module_line(ax=ax)
    ax = add_north_arrow(ax=ax)

    return fig


def add_north_arrow(
    ax,
    text="N",
    xy=(1.17, 1.1),
    text_color="black",
    arrow_color="black",
    fontsize=20,
    ha="center",
    va="center"
):
    """Add a north arrow to the map.

    Args:
        ax (returned from plot_heatmap())
        text (str, optional): Text for north arrow. Defaults to "N".
        xy (tuple, optional): Location of the north arrow. Each number
        representing the percentage length of the map from the upper-left
        cornor.
        arrow_length (float, optional): Length of the north arrow. Defaults to
        0.2 (20% length of the map).
        text_color (str, optional): Text color. Defaults to "black".
        arrow_color (str, optional): North arrow color. Defaults to "black".
        fontsize (int, optional): Text font size. Defaults to 20.
        width (int, optional): Width of the north arrow. Defaults to 5.
        headwidth (int, optional): head width of the north arrow. Defaults 15.
        ha (str, optional): Horizontal alignment. Defaults to "center".
        va (str, optional): Vertical alignment. Defaults to "center".
    """
    yarrow = xy[1] - 0.05
    if APV_SystSettings.sceneDict['azimuth'] == 90 or \
            APV_SystSettings.sceneDict == 270:
        xy = (1, 1.3)
        yarrow = xy[1] - 0.15
    # North [N]
    ax.annotate(
        text,
        xy=xy,
        xytext=(xy[0], xy[1]),
        color=text_color,
        horizontalalignment='left',
        ha=ha,
        va=va,
        fontsize=fontsize,
        xycoords=ax.transAxes
    )
    # Arrow
    ax.text(
        xy[0],
        yarrow, "    ", ha=ha, va=va, rotation=90, size=10,
        bbox=dict(boxstyle='rarrow, pad=0.5', fc='black',
                  ec=arrow_color, lw=1), transform=ax.transAxes)

    return ax


def add_module_line(ax):
    ''' adds lines in heatmap to indicate PV modules location.


    '''
    # NOT READY! TODO insert geometry formulas for x1,y1,x2,y2
    sceneDict = APV_SystSettings.sceneDict
    moduleDict = APV_SystSettings.moduleDict
    # Field Geometry
    x_field = round(
        sceneDict['nMods'] * moduleDict['x'])
    y_field = round(
        sceneDict['pitch'] * (sceneDict['nRows']-1)
        + moduleDict['y'] * moduleDict['numpanels'])
    print('GEOMETRIES OF THE FIELD....\n', x_field, y_field)

    x1 = int(x_field/2)
    x2 = int(x_field/2)
    y1 = int(0)
    y2 = int(y_field + 2)
    print(x1, x2, y1, y2)
    # endy = y + length * math.sin(math.radians(angle))
    # endx = length * math.cos(math.radians(angle))

    # plot the points
    ax.plot([x1, x2], [5, 15], color='b', linestyle='-', linewidth=2)
    # ax.plot([20, 20], [0, 20])
    return


def comparing_plot_sns(
        df: pd.Series, x: str, y: str, unit: str, z='none',
        scatter_alpha=0.4, scatter_size=0.1,
        xy_min='default', xy_max='default'):

    df = df.dropna()
    if xy_max == 'default':
        xy_max = max(df[x].max(), df[y].max())
    else:
        xy_max = xy_max

    if xy_min == 'default':
        xy_min = min(df[x].min(), df[y].min())
    else:
        xy_min = xy_min

    # linear regression #############
    slope, intercept, r, p_value, std_err = stats.linregress(df[x], df[y])

    # plotting ##############
    sns.set_theme(style='darkgrid')
    sns.set_context(
        {'font.family': 'STIXGeneral',
         'mathtext.fontset': 'stix',
         'font.size': 12})
    # set up joint grid data
    g = sns.JointGrid(data=df, x=x, y=y, size=5)

    # add 45° reference line
    g.ax_joint.plot(
        (xy_min, xy_max), (xy_min, xy_max), 'w', linewidth=1, zorder=1)
    # add reg plot to main plot area with line_kws for customizations
    g.plot_joint(
        sns.regplot,
        line_kws={'color': 'k',
                  'alpha': 0.9,
                  'label': ('slope: {0:.2f}, '
                            'intercept: {1:.2f}, '
                            'R$^2$: {2:.2f}'
                            ).format(slope, intercept, r**2)},
        scatter_kws={'alpha': scatter_alpha, 's': scatter_size,
                     'zorder': 2
                     })

    # ####################################
    # RMSE and MBE
    mbe, rel_mbe, rmse, rel_rmse = apv.utils.evaluation.calc_RMSE_MBE(
        df[x], df[y])

    # add text annotation
    g.ax_joint.text(
        xy_min+0.05*xy_max, xy_max*0.95,
        ('MBE: {0:.2f}{1}\nRMSE: {2:.2f}{1}\n'
         'rel. MBE: {3:.2f}\nrel. RMSE: {4:.2f}\n'
         '(rel. to (max-min)/2)'
         ).format(mbe, unit, rmse, rel_mbe, rel_rmse),
        horizontalalignment='left', verticalalignment='top',
        size='medium', color='black', backgroundcolor="w",
        fontsize=11
        # weight='semibold'
    )
    # ####################################

    # add histograms to top and right side of the plot
    g.plot_marginals(sns.histplot)

    # plot legend
    g.ax_joint.legend(loc='lower right')
    g.ax_joint.set_xlim(xy_min, xy_max)
    g.ax_joint.set_ylim(xy_min, xy_max)

    return g


def comparing_plot_hv(
        df: pd.Series, x: str, y: str, z='none',
        xy_min='default', xy_max='default',
        interactive=False):

    if xy_max == 'default':
        xy_max = max(df[x].max(), df[y].max())
    else:
        xy_max = xy_max

    if xy_min == 'default':
        xy_min = min(df[x].min(), df[y].min())
    else:
        xy_min = xy_min

    if interactive:
        # setting bokeh as backend
        hv.extension('bokeh')
        vdims = [y] + df.columns.to_list()
        tooltips = [(col_name, '@'+col_name) for col_name in df.columns]
    else:
        hv.extension('matplotlib')
        vdims = [y]

    scatter = hv.Scatter(df, kdims=[x], vdims=vdims)

    scatter.opts(show_grid=True,  # width=600, height=500,
                 xlim=(0, xy_max), ylim=(0, xy_max), alpha=0.2)

    if interactive:
        scatter.opts(tools=[HoverTool(tooltips=tooltips)])
    if z is not 'none':
        scatter.opts(color=z, cmap='fire', colorbar=True,
                     colorbar_opts={'title': z})
    # red 45° line
    slope = hv.Slope(1, 0)
    slope.opts(color='red', line_width=0.5)
    #

    return scatter * slope


def plotStyle(
        width_to_height_ratio=1.618, fig_width_in_mm=90,
        plotline_width_in_pt='default',
        marker_size_in_pt='default',
        font_size=12):

    params = {
        'figure.figsize': (
            fig_width_in_mm/25.4,  # from pt to mm
            (fig_width_in_mm/25.4) / width_to_height_ratio
        ),
        'font.size': font_size,
        'font.family': 'STIXGeneral',
        'mathtext.fontset': 'stix',
    }

    if plotline_width_in_pt != 'default':
        params.update({
            'lines.linewidth': plotline_width_in_pt,
            'lines.markeredgewidth': 0.55*plotline_width_in_pt})

    if marker_size_in_pt != 'default':
        params.update({'lines.markersize': marker_size_in_pt})

    plt.rcParams.update(params)
    plt.rcParams['svg.fonttype'] = 'none'  # makes the text in the
    # exported plot real text, which editable in the svg in inkscape


plotStyle(fig_width_in_mm=220, width_to_height_ratio=1, marker_size_in_pt=1)

# setting bokeh as backend
hv.extension('bokeh')

# going to use show() to open plot in browser
renderer = hv.renderer('bokeh')

# Define stream linked to axis XY-range
range_stream = RangeXY(x_range=(-1., 1.), y_range=(-1., 1.))

# Create DynamicMap to compute fractal per zoom range and
# adjoin a logarithmic histogram
""" dmap = hv.DynamicMap(get_fractal, label='Manderbrot Explorer',
                     streams=[range_stream]).hist(log=True)

# Apply options
dmap.opts(
    opts.Histogram(framewise=True, logy=True, width=200, xlim=(1, None)),
    opts.Image(cmap='fire', logz=True, height=600, width=600,
               xaxis=None, yaxis=None))


# use show() from bokeh
show(hv.render(dmap)) """
