# #
from matplotlib.axes import Axes
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns

from pathlib import Path
from aiana.classes.util_classes.settings_handler import Settings
from aiana.classes.aiana_main import Aiana
from aiana.classes.weather_data import WeatherData
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
##

csv_files = []
subsets = list(su.titles.keys())
for subset in subsets:
    csv_files += [root /
                  (f'{subset}' + r"\cumulative\appended_GHI_as_TMY_aggfunc.csv")]


dfs = su.load_dfs_for_subplots(csv_files, labels=subsets)
##
# reference DLI (unshaded, from cumulative GHI):


def gather_dailyCumulated_GHI_refDLI(months: list) -> pd.DataFrame:
    # TODO store to file and read
    df = pd.DataFrame()
    #df.index.name = 'Month'
    settings = Settings()
    settings.sim.use_typDay_perMonth_for_irradianceCalculation = True
    for month in months:
        settings.sim.sim_date_time = f'{month:02}-15_12:00'
        df.loc[month, 'dCum_ghi[Wh m^-2]'] = \
            WeatherData(settings).dailyCumulated_ghi
        df.loc[month, 'refDLI'] = df.loc[month, 'dCum_ghi[Wh m^-2]']*0.0074034
    df['Month'] = df.index  # TODO why does df['Month']=month work only sometimes?
    return df

# #


def box_plot(dfs, subsets, titles=None, y="DLI", orient='horizontal',
             ref_y: pd.DataFrame = None):
    # TODO check out sns.catplot for subplots

    sns.set_theme(style="darkgrid")

    if orient == 'horizontal':
        plotting_utils.plotStyle(width_to_height_ratio=5.5, fig_width_in_mm=285)
        fig, axes = plt.subplots(
            1, len(subsets), sharex=True, sharey=True
        )
    else:
        plotting_utils.plotStyle(width_to_height_ratio=0.22, fig_width_in_mm=50)
        fig, axes = plt.subplots(
            len(subsets), 1, sharex=True, sharey=True
        )

    aiana = Aiana(Settings())
    for i, subset in enumerate(subsets):
        if titles is not None:
            axes[i].set_title(titles[i])

        df = dfs[dfs['label'] == subset]
        aiana.plotterObj.box_plot_month_comparing(
            df, axes[i], y=y, ref_y=ref_y)

        # axes limits
        if y == "ShadowDepth_cum":
            axes[i].set_ylim(20, 90)
        elif y == 'DLI':
            axes[i].set_ylim(0, 43)
        # axes labels

    if orient == 'horizontal':
        # hide_unwanted_axes_labels
        for i, ax in enumerate(axes):
            if i != int(len(axes)/2):
                ax.set(xlabel=None)
            if i != 0:
                ax.set(ylabel=None)
    else:
        # hide_unwanted_axes_labels
        for i, ax in enumerate(axes):
            if i != len(axes)-1:
                ax.set(xlabel=None)
            if i != int(len(axes)/2):
                ax.set(ylabel=None)

    # fig.tight_layout()
    fig.set_facecolor("white")
    fn = 'subset_boxplot.png'

    fi.save_fig(
        fig, Path(r'T:\Public\user\l.raumann_network\agri-PV\Poster') / f"{y}_{fn}",
        dpi=400, transparent=True)


ref_y = gather_dailyCumulated_GHI_refDLI([4, 6, 8, 10])
box_plot(dfs, subsets=subsets,  # titles=list(su.titles.values())
         ref_y=ref_y)


# #
