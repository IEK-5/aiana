import sys
import pytictoc
import pandas as pd
from pathlib import Path
from typing import Literal

import apv.utils.files_interface as fi
from apv.classes.br_wrapper import BR_Wrapper
from apv.classes.weather_data import WeatherData
from apv.classes.util_classes.sim_datetime import SimDT
from apv.classes.util_classes.settings_grouper import Settings
from apv.classes.util_classes.geometries_handler import GeometriesHandler


def adjust_settings(
        subset: Literal['std', 'std_glass', 'std_sw',
                        'checker_board', 'cell_gaps', 'roof_for_EW'],
        settings: Settings) -> Settings:
    # constant settings
    settings.sim.study_name = 'framed_APV_noBorderEffects'
    settings.sim.spatial_resolution = 0.05
    settings.sim.time_step_in_minutes = 3
    settings.sim.use_acceleradRT_view = True
    settings.sim.use_accelerad_GPU_processing = True

    ghObj = GeometriesHandler(settings)
    # name depending settings
    settings.apv.glass_modules = False
    settings.apv.module_form = 'std'
    settings.apv.sceneDict['nRows'] = 6
    settings.apv.sceneDict['azimuth'] = 180
    settings.apv.mountingStructureDict.update({
        'n_apv_system_clones_in_x': 3,
        'n_apv_system_clones_in_negative_x': 3})
    settings.apv.gScan_area.update({
        'ground_scan_margin_y': -2*settings.apv.sceneDict['pitch']
        - ghObj.singleRow_footprint_y/2,
        'ground_scan_shift_y': settings.apv.sceneDict['pitch']
        + settings.apv.mountingStructureDict['post_thickness_y']/2,
    })

    if subset == 'std_sw':
        settings.apv.sceneDict['azimuth'] = 225

    elif subset == 'roof_for_EW':
        settings.apv.module_form = 'roof_for_EW'
        settings.apv.sceneDict['azimuth'] = 90
        settings.apv.sceneDict['nRows'] = 8
        settings.apv.sceneDict['nRows'] = 8
        # TODO x and y scale need to be swapped to be strict?
        settings.apv.gScan_area.update({
            'ground_scan_margin_y': -3*settings.apv.sceneDict['pitch']
            - ghObj.singleRow_footprint_y/2,
            'ground_scan_shift_x': ghObj.scan_length_x,
            'ground_scan_shift_y': 0})
        settings.apv.mountingStructureDict.update({
            'n_apv_system_clones_in_x': 2,
            'n_apv_system_clones_in_negative_x': 2})

    elif subset == 'std_glass':
        settings.apv.glass_modules = True

    elif subset == 'checker_board':
        settings.apv.glass_modules = True
        # settings.apv.framed_modules = True
        settings.apv.module_form = 'checker_board'
        settings.apv.cellLevelModuleParams.update({
            'xcellgap': 0, 'ycellgap': 0
        })

    elif subset == 'cell_gaps':
        settings.apv.glass_modules = True
        settings.apv.module_form = 'cell_gaps'
        settings.apv.cellLevelModuleParams.update({
            'xcellgap': 0.03, 'ycellgap': 0.03  # NOTE mohd hatte 0.02
        })
    elif subset != 'std':
        sys.exit('This subset does not exist.')
    return settings


def adjust_APVclone_count(settings: Settings, hour: int) -> Settings:
    # To reduce sim time
    if settings.apv.module_form != 'roof_for_EW':
        if hour <= 13:
            settings.apv.mountingStructureDict.update({
                'n_apv_system_clones_in_x': 3,
                'n_apv_system_clones_in_negative_x': 1})
        elif hour > 13:
            settings.apv.mountingStructureDict.update({
                'n_apv_system_clones_in_x': 1,
                'n_apv_system_clones_in_negative_x': 3})
    return settings


def create_results_subfolderPath(
        month: int, settings: Settings, subset: str) -> Path:
    return Path(
        settings.sim.study_name,
        f'res-{settings.sim.spatial_resolution}m'
        + f'_step-{settings.sim.time_step_in_minutes}min',
        subset,
        f'month-{month}'
    )


titles = {'std': 'Standard S',
          'std_sw': 'Standard SW',
          'checker_board': 'Checker board S',
          'cell_gaps': 'Cell gaps S',
          'roof_for_EW': 'Roof (std) EW'}
