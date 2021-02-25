# #
import importlib as imp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pvlib import shading, irradiance
import seaborn as sns
import apv.tools.simulation

imp.reload(apv.tools.simulation)

parameters = apv.tools.simulation.Parameters('fine')
df = apv.tools.simulation.create_parameters_permutated_df(parameters)
# #

for sim_ID in df.index:
    tilt = df.loc[sim_ID,'tilt']
    gcr = df.loc[sim_ID,'gcr']
    psi = shading.masking_angle_passias(tilt, gcr)
    # psi is the angle between a line parralel to the horizont
    # and a line from a point on the shadowed module
    # to the upper edge of the shadowing module
    # psi is averaged along the shadowed module resulting in an error < 1 %
    shading_loss = shading.sky_diffuse_passias(psi)
    transposition_ratio = irradiance.isotropic(tilt, dhi=1.0)
    df.loc[sim_ID, 'rel_dif_ir'] = transposition_ratio * (1-shading_loss) * 100  # %
df

# #

def plot_heatmap(df:pd.DataFrame, x:str, y:str, z:str):
    f, ax = plt.subplots(1,1, figsize=(8, 4))
    data = df.pivot(y, x, z)
    cm = 'inferno'
    ax = sns.heatmap(data, annot=False, linewidths=0, ax=ax, cmap=cm, cbar_kws={'label': z})
    ax.invert_yaxis()
    xlabels = ['{:.2f}'.format(float(item.get_text()))\
        for item in ax.get_xticklabels()]

    ax.set_xticklabels(xlabels)
    ax.set_yticklabels(ax.get_yticklabels(), rotation = 0)
    #plt.suptitle(title_extension+' min_bet_rate: '+str(min_bet_rate), y=0.93)

plot_heatmap(df, 'gcr', 'tilt', 'rel_dif_ir')
