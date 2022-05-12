import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
from pandas.core.frame import DataFrame
import seaborn as sns
import joypy
from scipy import stats
import apv
from apv.utils import RMSE_MBE


def plot_heatmap(
        df: pd.DataFrame,
        x: str,
        y: str,
        c: str,
        x_label=None,
        y_label=None,
        z_label=None,
        plot_title='',
        cm='inferno',
        ticklabels_skip_count_number="auto",
        vmin=None,
        vmax=None,
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
        vmin, vmax (float): color bar limits.

    Returns:
        Figure: matplotlib.figure.Figure object, which can be modified
        or saved later.
    """

    # prepare and print heatmap-input data for inspection
    print(df.nunique())
    data = df.pivot(y, x, c)

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
        z_label = c

    sns.heatmap(
        data,
        annot=False,
        linewidths=0,
        ax=ax,  # only relevant for later if there are more than one ax
        square=True,
        xticklabels=ticklabels_skip_count_number,
        yticklabels=ticklabels_skip_count_number,
        cmap=cm,
        cbar_kws={'label': z_label},
        vmin=vmin, vmax=vmax,
    )
    # To resemble Radiance coordinates
    ax.invert_yaxis()

    # overwrites x and y labels given by seaborn
    ax.tick_params()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    # x,y tick labels format and rotation
    xlabels = ['{:.1f}'.format(float(item.get_text()))
               for item in ax.get_xticklabels()]
    ylabels = ['{:.1f}'.format(float(item.get_text()))
               for item in ax.get_yticklabels()]
    ax.set_xticklabels(xlabels, rotation=0)
    ax.set_yticklabels(ylabels, rotation=0)

    # add_module_line(ax=ax)
    return fig


def add_north_arrow(
    ax,
    text="N",
    xy=(1.4, 1.3),
    text_color="black",
    arrow_color="black",
    fontsize=12,
    ha="center",
    va="center",
    panel_azimuth=180,
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

    # text "N"
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
    # arrow rotation = 90 --> pointing upwards
    # (north upwards for panel_azimuth = 180)
    # for panel south-west orientation, arrow has to point to upper left corner
    arrow_rotation = panel_azimuth-180 + 90

    ax.text(
        xy[0],
        xy[1] - 0.1, "    ", ha=ha, va=va, rotation=arrow_rotation, size=5,
        bbox=dict(boxstyle='rarrow, pad=0.4', fc='black',
                  ec=arrow_color, lw=0.5), transform=ax.transAxes)

    return ax


def Ridge_plot(data, seperate_by='Month', column='ShadowDepth_cum',
               color='#eb4d4b', xlabel='Shadow depth [%]'):
    """Creates multiple Kernel Denisty Plots by grouping data

    Args:
        data ([DataFrame]): Contains column to plot and column to group by
        seperate_by (str, optional): Element to group by. Defaults to 'Month'.
        column (str, optional): column of the df. Defaults to 'ShadowDepth_cum'.
        color (str, optional): Red. Defaults to '#eb4d4b'.
        xlabel (str, optional): according to column. Defaults to 'Shadow depth [%]'.

    Returns:
        Figure: Kernel denisty function for each month
    """

    fig, axes = joypy.joyplot(data=data, by=seperate_by,
                              column=column,
                              color=color, fade=False, grid=True,
                              xlabels=True, ylabels=True, alpha=0.85)
    plt.xlabel(xlabel)
    plt.ylabel(seperate_by)

    return fig, axes


# snippet (not ready) for drawing module position into heatmap,
# probably not needed anymore since we can see the post position as dark pixel
""" def add_module_line(ax):
    ''' adds lines in heatmap to indicate PV modules location.
    '''
    # insert geometry formulas for x1,y1,x2,y2
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
    return """


def comparing_plot_sns(
        df: pd.Series, x: str, y: str, unit=' [-]', hue=None,
        scatter_alpha=0.4, scatter_size=0.1,
        xy_min='default', xy_max='default', title=''):

    df = df.dropna(subset=[x, y])
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

    # regression line and scatter plot: ###
    # add reg plot to main plot area with line_kws for customizations
    g.plot_joint(
        sns.regplot,
        line_kws={'color': 'k',
                  'alpha': 0.5,
                  'label': ('slope: {0:.3f}, '
                            'intercept: {1:.3f}, '
                            'R$^2$: {2:.3f}'
                            ).format(slope, intercept, r**2)},
        scatter_kws={'alpha': scatter_alpha, 's': scatter_size,
                     'zorder': 2,  # 'hue': hue
                     })

    # ####################################
    # RMSE and MBE
    mbe, rel_mbe, rmse, rel_rmse = RMSE_MBE.calc_RMSE_MBE(df[x], df[y])

    # add text annotation
    g.ax_joint.text(
        xy_min+0.5*(xy_max-xy_min), xy_max-0.5*(xy_max-xy_min),
        ('MBE: {0:.3f}{1}\nRMSE: {2:.3f}{1}\n'
         'rel. MBE: {3:.3f}\nrel. RMSE: {4:.3f}\n'
         '(rel. to (max-min)/2)'
         ).format(mbe, unit, rmse, rel_mbe, rel_rmse),
        horizontalalignment='left', verticalalignment='top',
        color='black', backgroundcolor="w",
        fontsize=11
        # weight='semibold'
    )
    # ####################################

    # add histograms to top and right side of the plot
    g.plot_marginals(sns.histplot)

    # title
    # g.ax_joint.set_title(title) # --> is covered by upper hist plot

    g.ax_joint.text(
        xy_min+0.2*(xy_max-xy_min), xy_max-0.1*(xy_max-xy_min),
        title,
        color='black', backgroundcolor="w",
        fontsize=12
        # weight='semibold'
    )

    # plot legend
    g.ax_joint.legend(loc='lower right')
    g.ax_joint.set_xlim(xy_min, xy_max)
    g.ax_joint.set_ylim(xy_min, xy_max)

    return g


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


# plotStyle(fig_width_in_mm=220, width_to_height_ratio=1, marker_size_in_pt=1)
