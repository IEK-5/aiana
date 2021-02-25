import matplotlib.pyplot as plt
import holoviews as hv
from holoviews import opts
from holoviews.streams import RangeXY
from bokeh.plotting import show


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
