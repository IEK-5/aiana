##''
import core as core_module
import importlib as imp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#import os as os
#from datetime import datetime as dt
#import time as t
#import json
#from tqdm.auto import trange, tqdm
import itertools
##''
#pd.Timestamp('2020-10-26 00:00:00').tz_localize(tz='CET')

class Parameters():    
    def __init__(self, resolution:str):

        if resolution == 'fine':          
            self.tilt = np.arange(0, 56, 2)
            #self.azimut = np.arange(150, 211, 1)
            self.gcr = np.arange(0.1, 1.01, 0.05) #ground covering ratio

        if resolution == 'coarse':          
            self.tilt = np.arange(15, 56, 15)
            #self.azimut = np.arange(150, 211, 15)
            self.gcr = np.arange(0.5, 1.001, 0.25) #ground covering ratio

def list_parameters(parameters, exclude=[]):
    parameter_list = []
    for attribute in dir(parameters):
        if not attribute.startswith('__') and not callable(
            getattr(parameters, attribute)):

            if attribute not in exclude:
                parameter_list += [attribute] 
    return parameter_list 

def create_parameters_permutated_df(parameters, parameters_list:list)->pd.DataFrame:     
    parameter_ranges = []
    for attribute in parameters_list:   
        parameter_ranges += [getattr(parameters, attribute)]

    data = list(itertools.product(*parameter_ranges))
    sim_IDs = range(1, len(data)+1)
    #fill in config attributes into the dataframe
    df = pd.DataFrame(data, index=sim_IDs, columns=parameters_list)
    df.index.names = ['sim_ID']  
    return df
##''
parameters = Parameters('fine')
parameters_list = list_parameters(parameters)
df = create_parameters_permutated_df(parameters, parameters_list)
##''

from pvlib import shading, irradiance

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

##''
import seaborn as sns       

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

##''
plot_heatmap()
##''
plt.plot(tilt, relative_diffuse_irradiance, label=f'gcr = {gcr}')

plt.xlabel('Module inclination angle [degrees]')
plt.ylabel('Relative diffuse irradiance [%]')
#plt.ylim(0, 105)
plt.legend()
plt.show()
##''
