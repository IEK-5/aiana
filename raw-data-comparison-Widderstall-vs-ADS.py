##''
import core as core_module
import importlib as imp
import pandas as pd
import matplotlib.pyplot as plt

##''
'''
the "ads" data is satelite based and from https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-solar-radiation-timeseries?tab=form
the "ws" data is from a ground station in Widderstall and from Barts file
'''
# api request for ads
import cdsapi
c = cdsapi.Client()
c.retrieve(
    'cams-solar-radiation-timeseries',
    {
        'sky_type': 'observed_cloud',
        'location': {
            'latitude': 48.533,
            'longitude': 9.717,
        },
        'altitude': '750',
        'date': '2015-01-01/2016-01-01',
        'time_step': '1minute',
        'time_reference': 'universal_time',
        'format': 'csv',
    },
    'download.csv')


##''
imp.reload(core_module)
cf = core_module.CoreFunctions()

##''
df_ws = cf.df_from_file('raw-data/sanyo', skiprows=9, append_all_in_folder=True,delimiter='\t')
df_ws = df_ws.set_index(pd.to_datetime(df_ws['Datum']))
# df_ws.index = df_ws.index.tz_localize('UTC').tz_convert('Europe/Berlin') #utc +1
df_ws.index.names = ['timestamp']
##''
df_ads = cf.df_from_file('raw-data/ads',skiprows=42, delimiter=';',append_all_in_folder=True)
##''

##''
def add_timestampIndex_equal_to_start_of_observation_period(
    df:pd.DataFrame,
    observation_period_header='Observation period'    
    )->pd.DataFrame:

    df_start_end = df[observation_period_header].str.split('/', expand=True)
    # set observation-start as index
    df = df.set_index(pd.to_datetime(df_start_end[0]))
    #df.index = df.index.tz_localize(tz='UTC')
    df.index.names = ['timestamp']

    return df

def average_var_to_timestamp_between_observation_periods(
    df:pd.DataFrame,
    variables:list,  
    )->pd.DataFrame:

    '''
    to eleminate around 4% deviations
    ''' 

    for variable in variables:
        # calculating an instantaneous value around the index-timestamp by taking the average
        # of the value for the previous period and the current period
        df[variable] = ((df[variable]+df[variable].shift(1))/2)

    return df

def add_missing_timestamp_indices(df):
    #get timedelta
    time_delta_min_str = str(int((df.index[1]-df.index[0]).total_seconds()/60))+'min'
    df_complete = df.resample(time_delta_min_str).mean()
    print(str(len(df)-len(df_complete))+' row(s) were missing and have been added.')
    return df_complete


# prepare data
df_ws = add_missing_timestamp_indices(df_ws)
df_ads = add_timestampIndex_equal_to_start_of_observation_period(df_ads)
df_ads = add_missing_timestamp_indices(df_ads)
variables = ['GHI','DHI']
df_ads = average_var_to_timestamp_between_observation_periods(
    df_ads, variables)


##''
#slice to 5 mins
df_ads2 = df_ads.iloc[::5].copy()
# one hour shift needed to take time zone differences into account
df_ads2.index = df_ads2.index.shift(12) 

#verify synchronity
plt.plot(df_ads2[:800].index, df_ads2[:800]['GHI']*60) 
plt.plot(df_ws[:800].index, df_ws[:800]['GHI'])
##''
df_ws.index

##''
def plot_comparison(variables:list, xy_max=1000):
    f, axs = plt.subplots(1,2, sharey=True)

    cf.plotStyle(fig_width_in_mm=220, width_to_height_ratio=2.2, marker_size_in_pt=1)

    for variable,ax in zip(variables, axs.ravel()):
        ax.plot(df_ws[variable], df_ads2[variable]*60, '+', alpha=0.3) #*60 to convert from W*hrs to W (1hr/1min = 3600s/60s)
        ax.set_xlabel('Widderstall')
        ax.set_ylabel('ADS')
        ax.set_title('$'+variable+'$ [W/m$^2$]')
        ax.set_xlim(0,xy_max)
        ax.set_ylim(0,xy_max)
        ax.grid()
        ax.plot((0,xy_max),(0,xy_max), c='r', linewidth=0.3)

    cf.save_fig(f, file_name='Widderstall_vs_ads_'+str(variables), rel_path='results', dpi=500)

plot_comparison(variables) 


##''
plot_comparison(variables, xy_max=400) 

##''
# RMS and bias
# note: substracting two dataframe works via the index values not their position 
# (via "loc" not via "iloc"). Therefore, the following is correct

df_meta = pd.DataFrame()
for variable in variables:
    df_meta.loc['root mean square error', variable] = ((df_ws[variable] - df_ads2[variable])**2).mean()**0.5
    df_meta.loc['mean bias error', variable] = (df_ws[variable] - df_ads2[variable]).mean()
df_meta


#df_meta.loc['delta_RMS',variable] = (df_ws[variable]**2).mean()**0.5 - (df_ads2[variable]**2).mean()**0.5
#df_meta.loc['bias',variable] = df_ws[variable].mean() - df_ads2[variable].mean()
 

