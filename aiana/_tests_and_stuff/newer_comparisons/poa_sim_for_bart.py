import pvlib
import aiana
import pandas as pd
import numpy as np

def sim_poa(df, model='isotropic'):
    df = aiana.utils.time.column_to_utc_index(df, 'Datum', 'Etc/GMT-1')

    # set GHI >= DHI (data contains GHI < DHI, which makes no sense):
    df['GHI'] = np.where(df['GHI'] < df['DHI'], df['DHI'], df['GHI'])
    # POA sim
    site = pvlib.location.Location(
        48.533, 9.717, altitude=750, tz='Europe/Berlin')

    # Get solar azimuth and zenith to pass to the transposition function
    solar_position = site.get_solarposition(times=df.index)

    # dni: pd.Series = (df['GHI'] - df['DHI']) / np.cos(
    #    solar_position['apparent_zenith']*np.pi/180)
    # (differences to following < e-15)
    dni = pvlib.irradiance.dni(
        df['GHI'], df['DHI'], solar_position['apparent_zenith'])

    df_POA_irradiance = pvlib.irradiance.get_total_irradiance(
        surface_tilt=40,    # from widderstall description file
        surface_azimuth=180,  # "
        # accounting for armospheric diffraction:
        solar_zenith=solar_position['apparent_zenith'],
        solar_azimuth=solar_position['azimuth'],
        dni=dni,
        ghi=df['GHI'],
        dhi=df['DHI'],
        model=model
    )

    df['POA_sim'] = df_POA_irradiance['poa_global']
    return df


for model in [
    # 'isotropic',
    'perez'
]:
    df = aiana.utils.files_interface.df_from_file_or_folder(
        r'C:\Users\l.raumann\Documents\agri-PV\raw-data\sanyo',
        skiprows=9, append_all_in_folder=True, delimiter='\t'
    )

    df = sim_poa(df, model=model)

    aiana.utils.files_interface.df_export(
        df, f'poa_widderstall_{model}', rel_path='processed-data')