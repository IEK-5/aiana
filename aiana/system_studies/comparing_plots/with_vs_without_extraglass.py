# #
import sys
import seaborn as sns
from typing import Literal
from matplotlib import pyplot as plt
import pandas as pd
from aiana.classes.weather_data import WeatherData
import pytictoc
from pathlib import Path
import os
from aiana.classes.util_classes.sim_datetime import SimDT
from aiana.classes.util_classes.settings_handler import Settings
from aiana.settings.apv_system_settings import APV_Syst_InclinedTables_S_Morschenich
from aiana.classes.aiana_main import Aiana
from aiana.utils import plotting_utils
import aiana.utils.files_interface as fi
from aiana.classes.rad_txt_related.geometries_handler import GeometriesHandler


def load_dfs(csv_files: list):
    dfs = []
    for file in csv_files:
        df = fi.df_from_file_or_folder(file)
        df['custom_index'] = df['xy']+'_M'+df['Month'].astype(str)
        df.set_index('custom_index', inplace=True)
        dfs += [df]
    return dfs


root: Path = Path(
    r"C:\Users\Leonard Raumann\Documents\agri-PV\results\framed_APV_noBorderEffects"
)
dfs = load_dfs([
    root / r"std_res-0.25m_step-6min\cumulative\appended_GHI_as_TMY_aggfunc.csv",
    root / r"std_glass_res-0.25m_step-6min\cumulative\appended_GHI_as_TMY_aggfunc.csv"
])
dfs
# #


def box_plot(fn, dfs, titles, y="ShadowDepth_cum"):
    fig, axes = plt.subplots(1, len(dfs))

    if len(dfs) > 1:
        for i, df in enumerate(dfs):
            sns.boxplot(x="Month", y=y,
                        data=df, palette="autumn", ax=axes[i])
            axes[i].set_title(titles[i])
            if y == "ShadowDepth_cum":
                axes[i].set_ylim(20, 90)
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


box_plot('glass_comparison.jpg', dfs, ['std', 'std_with_glass'], y='DLI')

box_plot('glass_comparison.jpg', dfs, ['std', 'std_with_glass'])
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
