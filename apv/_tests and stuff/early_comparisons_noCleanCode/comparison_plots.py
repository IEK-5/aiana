import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from scipy import stats
import holoviews as hv
from bokeh.models import HoverTool
from holoviews.streams import RangeXY


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
