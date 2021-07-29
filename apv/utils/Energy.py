''' Uses PVlib and Bifacial_Radiance to forecast electrical power, energy yield
and mismatch losses.
'''
# #
from pvlib import pvsystem
from pvlib.pvsystem import PVSystem
from pvlib.modelchain import ModelChain
import apv.resources.locations as loc
from apv.settings import Simulation as s
from apv.settings import UserPaths
from apv.utils import files_interface as fi
from apv.settings import Simulation as simSettingsObj


# #


def estimate_energy(simSettings: simSettingsObj,
                    met_data,
                    module_type,
                    time_stamp):
    # load metoerological data used by br_wrapper and location
    location = loc.APV_Morschenich
    tmy_data = met_data

    # load the scene paramaters from settings
    tilt_angle = s.geometries.sceneDict['tilt']
    azimuth_angle = s.geometries.sceneDict['azimuth']
    albedo = s.ground_albedo

    # Solar position
    sol_pos = pvlib.solarposition.get_solarposition(time_stamp,
                                                    location.latitude,
                                                    location.longitude,
                                                    location.altitude,
                                                    method='nrel_numpy')

    # DNI Extraterrestrial
    dni_extra = pvlib.irradiance.get_extra_radiation(time_stamp)

    # Calculate relative airmass
    air_mass = pvlib.atmosphere.get_relative_airmass(sol_pos['apparent_zenith'])

    # Calculate pressure
    air_press = pvlib.atmosphere.alt2pres(location.altitude)

    # Calculate absolute (corrected) airmass
    air_mass_abs = pvlib.atmosphere.get_absolute_airmass(air_mass, air_press)
    pvli


# #
estimate_energy()

# #
module = pvsystem.retrieve_sam('SandiaMod')
inverter = pvsystem.retrieve_sam('SandiaInverter')
temp_model = pvsystem.temperature.pvsyst_cell()
system = PVSystem(module_parameters=module,
                  inverter_parameters=inverter,
                  temperature_model_parameters=)
