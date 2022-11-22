""" This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>."""

"""Paths for working folder, radiance folder
"""
from pathlib import Path
from aiana.utils import files_interface as fi


class UserPaths:
    """more sub pathes can be overwritten later by accessing Simulation.paths
    as defined in classes/util_classes/settings_handler.py
    """

    # root
    root: Path = Path().home().resolve() / 'Documents/agri-PV'
    #root: Path = Path('T:/Public/user/l.raumann_network/agri-PV')

    # radiance input files (will contain files for geometries, sky, materials)
    radiance_input_files: Path = root / 'radiance_input_files'
    # for weather data
    weatherData_folder: Path = root / 'satellite_weatherData'
    # for plots and tables. See also utils/results_organizer.py
    results_parent_folder: Path = root / 'results'

    # check folder existence
    fi.make_dirs_if_not_there(
        [radiance_input_files, weatherData_folder, results_parent_folder]
    )
