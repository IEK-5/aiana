from pathlib import Path
from apv.utils import files_interface as fi
from apv.classes.util_classes.settings_grouper import Settings


def create_results_subfolder_path(settings: Settings):

    results_subfolder_path: Path = settings.paths.results_folder / Path(
        settings.names.study,
        settings.apv.module_form
        + f'_res-{settings.sim.spatial_resolution}m'
        + f'_step-{settings.sim.time_step_in_minutes}min'
        + f'_TMY_aggfunc-{settings.sim.TMY_irradiance_aggfunc}'
    )
    # check folder existence
    fi.make_dirs_if_not_there(results_subfolder_path)

    return results_subfolder_path
