##''
import importlib as imp
import numpy as np
import pandas as pd 
import os as os
import matplotlib.pyplot as plt
import pathlib2 as pl2
from datetime import datetime as dt
import time as t
import json
from tqdm.auto import trange, tqdm


##''

class CoreFunctions():
    path_main = os.path.abspath(
            os.path.join(os.path.dirname(__file__),'..','..')
        )

    #def __init__(self):

    def printNotes(cls, category=''):

        if category == 'df':
            print(
            '''            
            # df index filter:    
            df[df.index.isin(list_of_indices)]

            # df rename index / columns:
            df.index.names = ['name']  
            df.columns = ['name1','name2']

            # set index
            df = df.set_index(df['col_name'])

            # to select multiple columns use double []:
            df[['col1','col2']]

            # with concat and merge, all df combining types can be done, 
            # guide: https://towardsdatascience.com/combining-pandas-dataframes-the-easy-way-41eb0f2c1ebf
            # 
            # short cut: create new df with index = df1 and collumns from df2 joined 
            # for the same indices as in df1
            df = df1.join(df2)
            '''
            )

        else:
            print(
            '''
            import importlib as imp    
            imp.reload(core)

            # figure initialization:
                fig = plt.figure()
                ax1=fig.add_subplot(121, label="1") #numbers: first 2 numbers = "rows,colums" of complete plot, third number: where in the grid goring through rows and then through colums
                ax2=fig.add_subplot(122, label="2") #different labels for 2 x and 2 y axes in right subplot
                ax3=fig.add_subplot(122, label="3", frame_on=False)
            

            f, axs = plt.subplots(3,2, figsize=(12, 12), sharey=True)
            for z,ax in zip(z_list, axs.ravel()):
                ax.plot...
            
            '''
            )



    def df_settings(cls, max_columns = 30, max_rows = 40):
        pd.set_option('display.max_columns', max_columns)
        pd.set_option('display.max_rows', max_rows)

    def plotStyle(cls, width_to_height_ratio = 1.618, fig_width_in_mm = 90, 
            plotline_width_in_pt = 'default', marker_size_in_pt = 'default', font_size = 12):

        params = {
            'figure.figsize': (
                fig_width_in_mm/25.4, #from pt to mm
                (fig_width_in_mm/25.4) / width_to_height_ratio
                ),
            'font.size': font_size,
            'font.family': 'STIXGeneral',
            'mathtext.fontset': 'stix',
            }

        if plotline_width_in_pt != 'default':
            params.update({'lines.linewidth': plotline_width_in_pt,
                'lines.markeredgewidth': 0.55*plotline_width_in_pt})  

        if marker_size_in_pt != 'default':
            params.update({'lines.markersize': marker_size_in_pt})     
            
        plt.rcParams.update(params)
        plt.rcParams['svg.fonttype'] = 'none'# makes the text in the exported plot real text, which editable in the svg in inkscape 


##''
###### PLOT STYLING ######
#colors: black,red,blue,orange,violet,dark green as in matplotlib qualitative color map paired (only dark ones)
myColors={'k':(25/255,25/255,25/255),'r':(227/255,26/255,28/255),'b':(0/255,69/255,200/255),
         'o':(255/255,127/255,0/255),'v':(93/255,55/255,135/255),'g':(47/255,146/255,40/255)}


