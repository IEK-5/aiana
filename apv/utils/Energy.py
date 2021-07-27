''' Uses PVlib and Bifacial_Radiance to forecast electrical power, energy yield
and mismatch losses.
'''
# #
import pvlib
import apv.resources.locations as loc
from apv.settings import Simulation as s
from apv.settings import UserPaths
from apv.utils import files_interface as fi

# #


def estimate_energy(met_data,
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
