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

    def Join_relPath_toHomePath_AndMakeDirsIfNotThere(cls, rel_path:str, path_main = path_main):
        destiPath = os.path.join(path_main, rel_path)
        if not os.path.exists(destiPath):
            os.makedirs(destiPath)
            print('Created folder: ' + destiPath)        
        return destiPath

    def df_from_file(cls, rel_path:str, 
                    path_main = path_main,
                    skiprows=0,
                    index_col=None, delimiter ='\s+|\at+|\s+\t+|\t+\s+|,|;', 
                    append_all_in_folder=False,
                    names=None, header ='infer'):
        '''
        rel_path: relative file path with file extension,
        in case of append_all_in_folder=True: rel_path = folder path 
        and file extrionsion doesnt matter

        header=none if no header labels are there
        '''
        df = pd.DataFrame()

        def read_file(cls, source_file):
            print('reading ' + source_file.split('\\')[-1])
            return pd.read_csv(
                source_file,
                skiprows=skiprows, 
                delimiter=delimiter,
                index_col=index_col, 
                names=names, 
                header=header, 
                engine='python')  
        
        if append_all_in_folder == False:        
            source_file = os.path.join(path_main, rel_path)
            try:
                df = read_file(cls, source_file)
            except FileNotFoundError:
                folder_path = "/".join(source_file.split("\\")[:-1])        
                if os.path.exists(folder_path):
                    print("check filename: " + str(os.listdir(folder_path)))

        if append_all_in_folder == True: 
            source_folder = os.path.join(path_main, rel_path)
            source_files = []
            for file_name in os.listdir(source_folder):
                source_files += [os.path.join(path_main, rel_path, file_name)]
            #generator (as list comprehension but without storing the actual content, only what to loop, which is much faster)
            dfs = (
               read_file(cls, source_file) for source_file in source_files
            )
            df = pd.concat(dfs)
        return df

    def df_export(
        cls,
        df, 
        file_name, 
        rel_path='', 
        float_format='%1.3e', 
        index=True, 
        sep='\t', 
        header =True):
        '''
        header: to rename columns provide a list of strings here
        float_formats = '%1.2e' for scientific, '%1.2f for float with 2 after comma digits'
        '''
        desti_path = cls.Join_relPath_toHomePath_AndMakeDirsIfNotThere(rel_path)
        file_path = os.path.join(desti_path, file_name + '.csv')
        df.to_csv(file_path, float_format=float_format, index=index, sep=sep, header=header)
        print('exported df to ' + desti_path)


    def save_fig(cls, fig, file_name, rel_path = '', file_formats = ['.jpg'], dpi = 300, transparent = False):    
        
        desti_path = cls.Join_relPath_toHomePath_AndMakeDirsIfNotThere(rel_path) 
        
        for file_format in file_formats:
            file_path = os.path.join(desti_path, file_name + file_format)
            fig.savefig(file_path, bbox_inches = 'tight', 
                        dpi = dpi, transparent = transparent)
            print('saved fig ' + file_path)

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


