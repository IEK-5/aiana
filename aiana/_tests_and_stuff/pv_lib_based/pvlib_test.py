# #
#import core as core_module
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
import importlib as imp
import numpy as np
import pandas as pd
import os as os
import matplotlib.pyplot as plt
import datetime as dt
import time as t
import json            # for parsing what binance sends back to us
from tqdm.auto import trange, tqdm

import pvlib

# #

naive_times = pd.date_range(start='2015', end='2016', freq='1h')


coordinates = [(40, -120, 'San Francisco', 10, 'Etc/GMT+8'),
               (52, 13, 'Berlin', 34, 'Etc/GMT-1'),
               (50.92, 6.36, 'Jülich', 83, 'Etc/GMT-1')]


sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

sapm_inverters = pvlib.pvsystem.retrieve_sam('cecinverter')

module = sandia_modules['Canadian_Solar_CS5P_220M___2009_']

module.DTC

# #


inverter = sapm_inverters['ABB__MICRO_0_25_I_OUTD_US_208__208V_']

temperature_model_parameters = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm'][
    'open_rack_glass_glass']


temp_air = 20

wind_speed = 0
# #

# #
################# procedual #################
system = {'module': module, 'inverter': inverter,
          'surface_azimuth': 180}

energies = {}
for latitude, longitude, name, altitude, timezone in coordinates:
    times = naive_times.tz_localize(timezone)
    system['surface_tilt'] = latitude
    solpos = pvlib.solarposition.get_solarposition(times, latitude, longitude)
    dni_extra = pvlib.irradiance.get_extra_radiation(times)
    airmass = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
    pressure = pvlib.atmosphere.alt2pres(altitude)
    am_abs = pvlib.atmosphere.get_absolute_airmass(airmass, pressure)
    tl = pvlib.clearsky.lookup_linke_turbidity(times, latitude, longitude)
    cs = pvlib.clearsky.ineichen(solpos['apparent_zenith'], am_abs, tl,
                                 dni_extra=dni_extra, altitude=altitude)
    aoi = pvlib.irradiance.aoi(system['surface_tilt'], system['surface_azimuth'],
                               solpos['apparent_zenith'], solpos['azimuth'])
    total_irrad = pvlib.irradiance.get_total_irradiance(system['surface_tilt'],
                                                        system['surface_azimuth'],
                                                        solpos['apparent_zenith'],
                                                        solpos['azimuth'],
                                                        cs['dni'], cs['ghi'], cs['dhi'],
                                                        dni_extra=dni_extra,
                                                        model='haydavies')
    tcell = pvlib.temperature.sapm_cell(total_irrad['poa_global'],
                                        temp_air, wind_speed,
                                        **temperature_model_parameters)
    effective_irradiance = pvlib.pvsystem.sapm_effective_irradiance(
        total_irrad['poa_direct'], total_irrad['poa_diffuse'],
        am_abs, aoi, module)
    dc = pvlib.pvsystem.sapm(effective_irradiance, tcell, module)
    # sapm = Sandia Array Performance Model
    ac = pvlib.inverter.sandia(dc['v_mp'], dc['p_mp'], inverter)
    # inverter = Wechselrichter (Gleichstrom zu Wechselstrom)
    # ac = alternating current, dc = direct current ?

    # v_mp = voltage at p_mp, p_mp = max power

    annual_energy = ac.sum()  # [W * h]
    energies[name] = annual_energy
energies = pd.Series(energies)
print(energies.round(0))

# #
################# object orientated #################


system = PVSystem(module_parameters=module,
                  inverter_parameters=inverter,
                  temperature_model_parameters=temperature_model_parameters)

energies = {}

for latitude, longitude, name, altitude, timezone in coordinates:
    times = naive_times.tz_localize(timezone)
    location = Location(latitude, longitude, name=name, altitude=altitude,
                        tz=timezone)
    weather = location.get_clearsky(times)
    mc = ModelChain(system, location,
                    orientation_strategy='south_at_latitude_tilt')
    mc.run_model(weather)
    annual_energy = mc.ac.sum()
    energies[name] = annual_energy

energies = pd.Series(energies)
print(energies.round(0))

# #
energies.plot(kind='bar', rot=0)
plt.ylabel('Yearly energy yield (W hr)')
# #
