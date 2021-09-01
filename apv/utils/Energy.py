''' Uses PVlib to forecast energy yield according to system settings.
'''
# #
from pandas.core.frame import DataFrame
import pvlib
from pathlib import Path
import pandas as pd
import os

from apv.settings.simulation import Simulation
import apv.settings.user_pathes as user_pathes
import apv.utils

# #


def estimate_energy(SimSettings, APV_SystSettings):

    # set time, weather, and location
    time_stamp = apv.utils.time.get_hour_of_year(
        SimSettings.sim_date_time)
    # read EPW data from bifacial radiance files
    epw = user_pathes.bifacial_radiance_files_folder / Path(
        'EPWs/')
    for file in os.listdir(epw):
        if file.endswith(".epw"):
            epw = user_pathes.bifacial_radiance_files_folder / Path(
                'EPWs/' + file)

    (tmydata, metadata) = pvlib.iotools.epw.read_epw(epw, coerce_year=2001)
    tmydata.index = tmydata.index+pd.Timedelta(hours=1)

    # Solar position
    sol_pos = pvlib.solarposition.get_solarposition(
        time_stamp,
        SimSettings.apv_location.latitude,
        SimSettings.apv_location.longitude,
        SimSettings.apv_location.altitude,
        method='nrel_numpy')

    # DNI Extraterrestrial from Day_of_year
    dni_extra = pvlib.irradiance.get_extra_radiation(time_stamp)
    # Calculate relative airmass
    air_mass = pvlib.atmosphere.get_relative_airmass(
        sol_pos['apparent_zenith'])
    # Calculate pressure
    air_press = pvlib.atmosphere.alt2pres(SimSettings.apv_location.altitude)
    # Calculate absolute (corrected) airmass
    air_mass_abs = pvlib.atmosphere.get_absolute_airmass(air_mass, air_press)
    # Create sky
    # x = f'2001-{SimSettings.sim_date_time[0:8]}'
    # time_stamp = (pd.to_datetime(x, format='%Y-%m-%d_%H'))
    naive_times = pd.date_range(start='2015', end='2016', freq='1h')
    turb = pvlib.clearsky.lookup_linke_turbidity(
        time=naive_times,
        latitude=SimSettings.apv_location.latitude,
        longitude=SimSettings.apv_location.longitude)
    perez_ineichen = pvlib.clearsky.ineichen(
        apparent_zenith=sol_pos['apparent_zenith'],
        airmass_absolute=air_mass_abs,
        linke_turbidity=turb,
        dni_extra=dni_extra,
        altitude=SimSettings.apv_location.altitude)

    # PV systems settings
    module = pvlib.pvsystem.retrieve_sam(f'{APV_SystSettings.module_name}')
    inverter = pvlib.pvsystem.retrieve_sam(
        'ABB__MICRO_0_25_I_OUTD_US_208__208V_')
    aoi = pvlib.irradiance.aoi(
        surface_tilt=APV_SystSettings.sceneDict['tilt'],
        surface_azimuth=APV_SystSettings.sceneDict['azimuth'],
        solar_zenith=sol_pos['apparent_zenith'],
        solar_azimuth=sol_pos['azimuth']
    )

    # Total irradiation on pv-system
    # TODO Use bifacial calculations
    # TODO total_irr2 = pvlib.bifacial.pvfactors_timeseries()
    total_irr = pvlib.irradiance.get_total_irradiance(
        surface_tilt=APV_SystSettings.sceneDict['tilt'],
        surface_azimuth=APV_SystSettings.sceneDict['azimuth'],
        solar_zenith=sol_pos['apparent_zenith'],
        solar_azimuth=sol_pos['azimuth'],
        dni=perez_ineichen['dni'], ghi=perez_ineichen['ghi'],
        dhi=perez_ineichen['dhi'], dni_extra=dni_extra, model='perez'
    )
    print(total_irr)

    temperature_model_parameters = pvlib.temperature\
        .TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

    tcell = pvlib.temperature.sapm_cell(total_irr['poa_global'],
                                        temp_air=epw.temp_air,
                                        wind_speed=epw.wind_speed,
                                        **temperature_model_parameters)
    effective_irr = pvlib.pvsystem.sapm_effective_irradiance(
        total_irr['poa_direct'], total_irr['poa_diffuse'], air_mass_abs,
        module)

    # Energy generated
    dc = pvlib.pvsystem.sapm(effective_irr, tcell, module)
    ac = pvlib.inverter.sandia(dc['v_mp'], dc['p_mp'], inverter)
    annual_energy = ac.sum()
    print(annual_energy)

    # TODO ammend power if checkerboard by /2

    return annual_energy
