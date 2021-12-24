"""Paths for working folder, radiance folder
"""

from pathlib import Path

root: Path = Path().home().resolve() / 'Documents/agri-PV'

# bifacial_radiance
# settings.UserPaths.br_folder
bifacial_radiance_files_folder: Path = root / 'bifacial_radiance_files'

# for plots and tables
results_folder: Path = root / 'results'
# for weather data
data_download_folder: Path = root / 'data_downloads'

# apv package location
apv_package: Path = Path(__file__).parent.parent.resolve()
