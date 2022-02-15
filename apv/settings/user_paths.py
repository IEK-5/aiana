"""Paths for working folder, radiance folder
"""

from pathlib import Path
from apv.utils import files_interface as fi
from apv.settings.file_names import Names


class UserPaths:

    def __init__(self, fileNames: Names):

        # root
        self.root: Path = Path().home().resolve() / 'Documents/agri-PV'

        # bifacial_radiance
        # settings.UserPaths.br_folder
        self.bifacial_radiance_files: Path = self.root \
            / 'bifacial_radiance_files'
        # for weather data
        self.data_download_folder: Path = self.root / 'data_downloads'

        # for plots and tables. See also utils/results_organizer.py
        self.results_folder: Path = self.root / 'results'

        # set csv file path for saving final merged results
        self.csv_parent_folder: Path = self.results_folder / 'data'

        self.csv_file_path: Path = self.csv_parent_folder /\
            f'ground_results_{fileNames.csv_fn}'

        # check folder existence
        fi.make_dirs_if_not_there([self.bifacial_radiance_files,
                                   self.data_download_folder,
                                   self.results_folder]
                                  )
