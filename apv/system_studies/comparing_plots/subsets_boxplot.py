# #
import sys
import seaborn as sns
from typing import Literal
from matplotlib import pyplot as plt
import pandas as pd
from apv.classes.weather_data import WeatherData
import pytictoc
from pathlib import Path
import os
from apv.classes.util_classes.sim_datetime import SimDT
from apv.classes.util_classes.settings_grouper import Settings
from apv.settings.apv_systems import APV_Syst_InclinedTables_S_Morschenich
from apv.classes.br_wrapper import BR_Wrapper
from apv.utils import plotting_utils
import apv.utils.files_interface as fi
from apv.classes.util_classes.geometries_handler import GeometriesHandler


root: Path = Path(
    r"C:\Users\Leonard Raumann\Documents\agri-PV\results\framed_APV_noBorderEffects"
)
csv_files = []
subsets = ['std', 'std_sw', 'checker_board', 'cell_gaps', 'roof_for_EW']
for subset in subsets:
    csv_files += [root /
                  (f'{subset}' + r"_res-0.25m_step-6min\cumulative\appended_GHI_as_TMY_aggfunc.csv")]


def load_dfs(csv_files: list):
    dfs = []
    for file in csv_files:
        df = fi.df_from_file_or_folder(file)
        print(file)
        df['custom_index'] = df['xy']+'_M'+df['Month'].astype(str)
        df.set_index('custom_index', inplace=True)
        df=df[df['Month']<12]
        dfs += [df]
    return dfs


dfs = load_dfs(csv_files)
dfs

# #
sns.set_theme(style="darkgrid", )
plotting_utils.plotStyle(fig_width_in_mm=180)


def box_plot(fn, dfs, titles, y="ShadowDepth_cum"):
    fig, axes = plt.subplots(1, len(dfs), sharey=True)
    if len(dfs) != len(titles):
        raise Exception("Title lengths does not fit to dfs length.")

    if len(dfs) > 1:
        for i, df in enumerate(dfs):
            sns.boxplot(x="Month", y=y,
                        data=df, palette="autumn", ax=axes[i],
                        )

            axes[i].set_title(titles[i])
            if y == "ShadowDepth_cum":
                axes[i].set_ylim(20, 90)
            if i > 0:
                axes[i].set(ylabel=None)
            axes[i].grid(True)
    else:
        sns.boxplot(x="Month", y=y, data=dfs[0], palette="autumn", ax=axes)
        axes.set_title(titles[0])
        if y == "ShadowDepth_cum":
            axes.set_ylim(20, 90)
        axes.grid(True)


    fig.tight_layout()
    fig.set_facecolor("white")
    fi.save_fig(fig, Path(root / f"{y}_{fn}"))

titles = ['standard S', 'standard SW', 'checker board S', 'cell gaps S', 'roof (std) EW']
filename_base = 'subset_boxplot.jpg'
box_plot(filename_base, dfs, titles, y='DLI')
# #
box_plot(filename_base, dfs, titles)
# #

# #
df_dif = dfs[0]
for y in ['DLI']:
    df_dif.loc[:, y] = dfs[1].loc[:, y]-dfs[0].loc[:, y]

# MBE, RMSE extra glass vs no extra glass

# evt nur unten relevant? denke schon, würde beschleunigen falls doch nötig
df_joined = dfs[0].join(dfs[1], rsuffix='_glass')
df_joined
# #
plotting_utils.comparing_plot_sns(df_joined, x='ShadowDepth_cum', y='ShadowDepth_cum_glass')

# #
g = plotting_utils.comparing_plot_sns(df_joined, x='DLI', y='DLI_glass',
                                      unit=' [mol / m²]')

fi.save_fig(g, root/f'comparing_plot_sns-month-all.jpg')
# #
for month in [6, 8, 10, 12]:
    df = df_joined[df_joined['Month'] == month]
    g = plotting_utils.comparing_plot_sns(df, x='DLI', y='DLI_glass',
                                          unit=' [mol / m²]',
                                          title=f'Month: {month}')
    fi.save_fig(g, root/f'comparing_plot_sns-month-{month}.jpg')
# #
