# #
import matplotlib
from matplotlib.axes import Axes
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
from pathlib import Path
from aiana.classes.util_classes.settings_handler import Settings
from aiana.classes.aiana_main import AianaMain
from aiana.utils import plotting_utils
from aiana.utils import files_interface as fi
from aiana.utils import study_utils as su

root: Path = Path(
    r"C:\Users\Leonard Raumann\Documents\agri-PV\results\framed_APV_noBorderEffects\res-0.05m_step-3min"
)

# concat (set to True if needed)
if False:
    for subset in list(su.titles.keys()):
        months = [4, 6, 8, 10]
        su.concat_months_for_box_plot(
            months, subset, fileNameSuffix='GHI_as_TMY_aggfunc',
            results_folder_cum=root / subset / 'cumulative')


csv_files = []
subsets = list(su.titles.keys())
for subset in subsets:
    csv_files += [root /
                  (f'{subset}' + r"\cumulative\appended_GHI_as_TMY_aggfunc.csv")]


dfs = su.load_dfs_for_subplots(csv_files, labels=subsets)
# #


def plot_ground_heatmaps_subplots(dfs: pd.DataFrame, subsets: list,
                                  month=6,
                                  to_get_colmap=False,
                                  subplot_orientation="horizontal"):
    if to_get_colmap is True:
        plotting_utils.plotStyle(
            width_to_height_ratio=1/4, fig_width_in_mm=120)
        subsets = subsets[:2]
        dpi = 600
        fn = f"heatmaps_4colbar.jpg"
    else:
        if subplot_orientation == "horizontal":
            plotting_utils.plotStyle(
                width_to_height_ratio=5, fig_width_in_mm=280)
            dpi = 400
            fn = f"heatmaps_{subplot_orientation}.png"
            north_arrow_xy = (-0.1, -0.1)
        else:
            plotting_utils.plotStyle(
                width_to_height_ratio=1/2, fig_width_in_mm=120)
            dpi = 400
            fn = f"heatmaps.png"
            north_arrow_xy = (-0.25, 0.15)

    # equal col bars
    dfs = dfs[dfs['Month'] == month]

    dfs['kWhm2'] = dfs['Whm2']/1000
    df_limits = dfs.agg([min, max])
    df_limits.loc['min', 'kWhm2'] = 1

    aiana = AianaMain(Settings())
    cb_orientation = "vertical"
    if subplot_orientation == "horizontal":
        fig, axes = plt.subplots(1, len(subsets),  # sharey=True
                                 )
        # cb_orientation="horizontal"
        #ax_cb = plt.axes([0.12, 0.88, 0.6, 0.08])
        ax_cb = plt.axes([0.91, 0.03, 0.015, 0.8])
    else:
        fig, axes = plt.subplots(len(subsets)+1, 1,   sharex=True
                                 )
        ax_cb = plt.axes([0.91, 0.12, 0.015, 0.7])

    norm = matplotlib.colors.Normalize(
        vmin=df_limits.loc['min', 'kWhm2'],
        vmax=df_limits.loc['max', 'kWhm2']
    )
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap='inferno'),
                      cax=ax_cb, label='Cumul. GGI [kWh m$^{-2}$]',
                      orientation=cb_orientation,
                      )
    cb.ax.xaxis.tick_top()
    ax_cb.annotate(
        'Cumul. GGI [kWh m$^{-2}$]',
        # xy=xy,
        xy=(0.8, 10),
        # color=text_color,
        # horizontalalignment='left',
        # ha=ha,
        # va=va,
        # fontsize=fontsize,
        # xycoords=ax.transAxes
    )

    for i, subset in enumerate(subsets):
        df = dfs[dfs['label'] == subset]
        axes[i] = plotting_utils.plot_heatmap(
            df=df, x='x', y='y', c='kWhm2',
            x_label='x [m]', y_label='y [m]',
            z_label='Cumulative\nGGI [kWh m$^{-2}$]',
            ticklabels_skip_count_number=40,
            tick_label_format='{:.0f}',
            vmin=df_limits.loc['min', 'kWhm2'],
            vmax=df_limits.loc['max', 'kWhm2'],
            ax_blanc=axes[i],
            show_colbar=False
        )
        # set azimuth for correct north arrow rotation:
        aiana.settings = su.adjust_settings(subset, aiana.settings)
        axes[i] = plotting_utils.add_north_arrow(
            axes[i], xy=north_arrow_xy, text="\n\n\n         N",
            panel_azimuth=aiana.settings.apv.sceneDict['azimuth']
        )

        axes[i].tick_params(left=True, bottom=True, length=2)

    # hide_unwanted_axes_labels

    for i, ax in enumerate(axes):
        if subplot_orientation == "horizontal":
            if i != int(len(axes)/2):
                ax.set(xlabel=None)
            if i != 0:
                ax.set(ylabel=None)
        else:
            if i != len(axes)-1:
                ax.set(xlabel=None)

    # fig.tight_layout()
    fi.save_fig(
        fig, Path(r'T:\Public\user\l.raumann_network\agri-PV\Poster') / fn,
        dpi=dpi, transparent=True)

    fig.show()


# horizontal
plot_ground_heatmaps_subplots(dfs, subsets=subsets,
                              subplot_orientation="horizontal")
# #
# vertically
for to_get_colmap in [False, True]:
    plot_ground_heatmaps_subplots(dfs, subsets=subsets,
                                  to_get_colmap=to_get_colmap)

# #
