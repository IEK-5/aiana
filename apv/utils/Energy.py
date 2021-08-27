''' Uses PVlib to forecast energy yield according to system settings.
'''
# #
import pvlib
from pathlib import Path
import pandas as pd
import os
from apv.settings import Simulation
from apv.settings import UserPaths
import apv.utils

# #


def estimate_energy(simSettings):
    # set time, weather, and location
    time_stamp = apv.utils.time.get_hour_of_year(
        simSettings.sim_date_time)
    # read EPW data
    epw = UserPaths.bifacial_radiance_files_folder / Path(
        'EPWs/')
    for file in os.listdir(epw):
        if file.endswith(".epw"):
            epw = UserPaths.bifacial_radiance_files_folder / Path(
                'EPWs/' + file)

    (tmydata, metadata) = pvlib.iotools.epw.read_epw(epw, coerce_year=2001)
    tmydata.index = tmydata.index+pd.Timedelta(hours=1)

    # Solar position
    sol_pos = pvlib.solarposition.get_solarposition(
        time_stamp,
        simSettings.apv_location.latitude,
        simSettings.apv_location.longitude,
        simSettings.apv_location.altitude,
        method='nrel_numpy')

    # DNI Extraterrestrial
    dni_extra = pvlib.irradiance.get_extra_radiation(time_stamp)

    # Calculate relative airmass
    air_mass = pvlib.atmosphere.get_relative_airmass(
        sol_pos['apparent_zenith'])

    # Calculate pressure
    air_press = pvlib.atmosphere.alt2pres(simSettings.apv_location.altitude)

    # Calculate absolute (corrected) airmass
    air_mass_abs = pvlib.atmosphere.get_absolute_airmass(air_mass, air_press)

    # Create sky
    turb = pvlib.clearsky.lookup_linke_turbidity(
        time=time_stamp,
        latitude=simSettings.apv_location.latitude,
        longitude=simSettings.apv_location.longitude)

    perez_ineichen = pvlib.clearsky.ineichen(
        apparent_zenith=sol_pos['apparent_zenith'],
        airmass_absolute=air_mass_abs,
        linke_turbidity=turb,
        dni_extra=dni_extra,
        altitude=simSettings.apv_location.altitude)

    # Module settings
    aoi = pvlib.irradiance.aoi(
        surface_tilt=simSettings.sceneDict['tilt'],
        surface_azimuth=simSettings.sceneDict['azimuth'],
        solar_zenith=sol_pos['apparent_zenith'],
        solar_azimuth=sol_pos['azimuth']
    )

    # Total irradiation on pv-system
    # TODO total_irr2 = pvlib.bifacial.pvfactors_timeseries()
    total_irr = pvlib.irradiance.get_total_irradiance(
        surface_tilt=simSettings.sceneDict['tilt'],
        surface_azimuth=simSettings.sceneDict['azimuth'],
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
    effective_irr = pvlib.pvsystem.sapm_effective_irradiance()
