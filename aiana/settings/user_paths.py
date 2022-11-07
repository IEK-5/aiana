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
    data_download_folder: Path = root / 'data_downloads'
    # for plots and tables. See also utils/results_organizer.py
    results_parent_folder: Path = root / 'results'

    # check folder existence
    fi.make_dirs_if_not_there(
        [radiance_input_files, data_download_folder, results_parent_folder]
    )
