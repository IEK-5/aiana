# #
from pandas.io.parsers import read_csv
from apv.utils.files_interface import save_fig
import pandas as pd
import apv.settings.user_pathes as user_pathes
from pathlib import Path
from datetime import datetime as dt
import numpy as np
import apv.utils.time as t
from matplotlib import pyplot as plt
from apv.utils.files_interface import save_fig

# #


def weather_to_csv(file_name='2010-2020_tst'):
    # Retrieve weather
    # TODO change file name
    path = user_pathes.bifacial_radiance_files_folder / Path(
        'EPWs/', f'{file_name}.csv')
    df = pd.read_csv(path, skiprows=43, header=None, sep=';', index_col=0,
                     parse_dates=True)
    column_names = ['TOA', ' Clear sky GHI', 'Clear sky BHI', 'Clear sky DHI',
                    'Clear sky BNI', 'GHI', 'BHI', 'DHI', 'BNI', 'Reliability']
    df.columns = column_names
    indx = df.index

    # define datetime index to resample
    time_index = []
    for i in np.arange(0, len(indx)):
        row = indx[i]
        x = dt.strptime(row[0:13], '%Y-%m-%dT%H')
        time_index.append(x)

    df['Datetime'] = pd.to_datetime(time_index)
    df.set_index('Datetime', inplace=True)

    # create average hour for each day per year
    x = df['GHI'].groupby([df.index.month, df.index.day, df.index.hour]).mean()
    y = df['DHI'].groupby([df.index.month, df.index.day, df.index.hour]).mean()
    x = x.reset_index(drop=True)
    y = y.reset_index(drop=True)

    if len(x) == 8784 and len(y) == 8784:
        a = t.get_hour_of_year('2-28_23h') + 1
        rg = np.arange(a, a+24)

        x.drop(index=rg, axis=0, inplace=True)
        y.drop(index=rg, axis=0, inplace=True)

    savedata = {'GHI': x, 'DHI': y}
    pd.DataFrame(savedata)
    csvfile = user_pathes.bifacial_radiance_files_folder / Path(
        'EPWs/', f'own_TMY_{file_name}.csv')
    savedata = pd.DataFrame(savedata)
    savedata.to_csv(csvfile, index=False, header=False, sep=' ',
                    columns=['GHI', 'DHI'])

    return savedata


# #
weather_to_csv()
# #
df = pd.read_csv(
    r"C:\Users\moham\Documents\agri-PV\bifacial_radiance_files\EPWs\own_TMY_2010-2020_tst.csv",
    sep=' ')
df.columns = ['GHI', 'DHI']
df2 = pd.read_csv(
    r"C:\Users\moham\Documents\agri-PV\bifacial_radiance_files\EPWs\epw_temp.csv", sep=' ')
df2.columns = ['GHI', 'DHI']
df.tail(5)

# #
file_name = '2010-2020_tst'
fig, ax1 = plt.subplots(1, 1)
ax1.set_xlabel('hour of year')

ax1.set_ylabel('Wh m$^ {-2}$')
ax1.set_title(f'Comparison of GHI between Own-TMY and EPW \n \
              {file_name}')

ax1.plot(df['GHI'])
ax1.plot(df2['GHI'],  alpha=0.5)
fig.legend(('Own-GHI', 'EPW-GHI'))
save_fig(fig, f'GHI-{file_name}-comparison TMY', transparent=False)

# #
fig2, ax2 = plt.subplots(1, 1)
ax2.set_xlabel('hour of year')

ax2.set_ylabel('Wh m$^ {-2}$')
ax2.set_title(f'Comparison of DHI between Own-TMY and EPW \n \
              Own-TMY {file_name}')

ax2.plot(df['DHI'])
ax2.plot(df2['DHI'],  alpha=0.5)
fig2.legend(('Own-DHI', 'EPW-DHI'))
save_fig(fig2, f'DHI-{file_name}-comparison TMY', transparent=False)
# #
fig3, ax3 = plt.subplots(1, 1)
ax3.set_xlabel('hour of year')

ax3.set_ylabel('Wh m$^{-2}$')
ax3.set_title(f'Comparison of DHI between Own-TMY and EPW \n \
              Own-TMY {file_name}')

ax3.scatter(df.index, df['DHI'], marker='v')
ax3.scatter(df.index, df2['DHI'],  alpha=0.8, marker="_")
fig3.legend(('Own-DHI', 'EPW-DHI'))
save_fig(fig3, f'DHI-{file_name}-comparison TMY', transparent=False)

# #
