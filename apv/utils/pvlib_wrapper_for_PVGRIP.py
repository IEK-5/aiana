# #
import pvlib
import pandas as pd
from typing import Literal


def get_IV_curve_data(
        pv_module_name, poa_global, temp_air, wind_speed,
        pv_module_database: Literal['SandiaMod', 'CECMod'] = 'SandiaMod'
):
    """
    Parameters
    ----------
    pv_module_name : str
        PV module name within the pv_module_database (see below).
        The method prints a list of valid names if the name cannot be found.

    poa_global : float or pd.Series
        Total incident irradiance [W/m^2].

    temp_air : float or pd.Series
        Ambient dry bulb temperature [C].

    wind_speed : float or pd.Series
        Wind speed at a height of 10 meters [m/s].

    pv_module_database : str
        optional. 'SandiaMod' or 'CECMod'. Defaults to 'SandiaMod'.


    Returns
    -------
    OrderedDict (float input) or DataFrame (series input) with:

        * i_sc : Short-circuit current (A)
        * i_mp : Current at the maximum-power point (A)
        * v_oc : Open-circuit voltage (V)
        * v_mp : Voltage at maximum-power point (V)
        * p_mp : Power at maximum-power point (W)
        * i_x : Current at module V = 0.5Voc, defines 4th point on I-V
          curve for modeling curve shape
        * i_xx : Current at module V = 0.5(Voc+Vmp), defines 5th point on
          I-V curve for modeling curve shape"""

    # load pv module database
    pv_modules: pd.DataFrame = pvlib.pvsystem.retrieve_sam(
        pv_module_database)
    pv_module_names: list = pv_modules.columns

    # extrac pv module
    if pv_module_name not in pv_module_names:
        return print('\nPV module name not found. List of valid names:'
                     f'\n{pv_module_names}')

    pv_module: pd.Series = pv_modules[pv_module_name]

    # calculate cell temperature
    temp_cell = pvlib.temperature.sapm_cell(
        poa_global, temp_air, wind_speed,
        pv_module['A'], pv_module['B'], pv_module['DTC']
    )
    # return IV curve data
    return pvlib.pvsystem.sapm(poa_global, temp_cell, pv_module)


if __name__ == '__main__':
    print(get_IV_curve_data('Advent_Solar_AS160___2006_', 900, 20, 5))
