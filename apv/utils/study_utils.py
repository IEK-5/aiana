# #
import sys
import pytictoc
import pandas as pd
from pathlib import Path
from typing import Literal

import apv.utils.files_interface as fi
from apv.classes.util_classes.settings_handler import Settings
from apv.classes.util_classes.geometries_handler import GeometriesHandler


def adjust_settings(
        subset: Literal['std', 'std_glass', 'std_sw',
                        'checker_board', 'cell_gaps', 'roof_for_EW'],
        settings: Settings) -> Settings:
    # constant settings
    settings.sim.study_name = 'framed_APV_noBorderEffects'
    settings.sim.spatial_resolution = 0.05
    settings.sim.time_step_in_minutes = 3

    ghObj = GeometriesHandler(settings)
    # name depending settings
    settings.apv.glass_modules = False
    settings.apv.module_form = 'std'
    settings.apv.sceneDict['nRows'] = 6
    settings.apv.sceneDict['azimuth'] = 180
    settings.apv.mountingStructureDict.update({
        'n_apv_system_clones_in_x': 3,
        'n_apv_system_clones_in_negative_x': 3})
    settings.apv.gScanAreaDict.update({
        'ground_scan_shift_x': 0,  # forgetting this at first messed me up
        'ground_scan_shift_y': settings.apv.sceneDict['pitch']
        + settings.apv.mountingStructureDict['post_thickness_y']/2,
        'ground_scan_margin_y': -2*settings.apv.sceneDict['pitch']
        - ghObj.singleRow_footprint_y/2,
    })
    match subset:
        case 'std':
            return settings
        case 'std_sw':
            settings.apv.sceneDict['azimuth'] = 225
            settings.apv.gScanAreaDict.update({'ground_scan_shift_y': 0})
        case 'roof_for_EW':
            settings.apv.module_form = 'roof_for_EW'
            settings.apv.sceneDict['azimuth'] = 90
            settings.apv.sceneDict['nRows'] = 8
            # TODO x and y scale need to be swapped to be strict?
            settings.apv.gScanAreaDict.update({
                'ground_scan_shift_x': ghObj.scan_length_x,
                'ground_scan_shift_y': 0,
                'ground_scan_margin_y': -3*settings.apv.sceneDict['pitch']
                - ghObj.singleRow_footprint_y/2})
            settings.apv.mountingStructureDict.update({
                'n_apv_system_clones_in_x': 2,
                'n_apv_system_clones_in_negative_x': 2})

        case 'std_glass':
            settings.apv.glass_modules = True

        case 'checker_board':
            # settings.apv.framed_modules = True
            settings.apv.glass_modules = True
            settings.apv.module_form = 'checker_board'
            settings.apv.cellLevelModuleParams.update({
                'xcellgap': 0, 'ycellgap': 0
            })

        case 'cell_gaps':
            settings.apv.glass_modules = True
            settings.apv.module_form = 'cell_gaps'
            settings.apv.cellLevelModuleParams.update({
                'xcellgap': 0.03, 'ycellgap': 0.03  # NOTE mohd hatte 0.02
            })
        case _:
            sys.exit('This subset does not exist.')
    return settings


def adjust_APVclone_count(settings: Settings, hour: int) -> Settings:
    # To reduce sim time
    if settings.apv.module_form not in ['std_sw', 'roof_for_EW']:
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
          'cell_gaps': 'Cell gaps S',
          'checker_board': 'Checker board S',
          'std_sw': 'Standard SW',
          'roof_for_EW': 'Roof (std) EW'}


def get_cum_csv_path(month: int, subset: str, results_folder_cum: Path
                     # compare_GGI_to
                     ) -> Path:
    # - {compare_GGI_to}'
    cum_file_name = subset+'_cumulated day 15th' + f' in month {month:02}'
    cum_csv_path = results_folder_cum / f'{cum_file_name}.csv'
    return cum_csv_path


def concat_months_for_box_plot(
        months: list, subset: str, fileNameSuffix: str, results_folder_cum: Path
) -> pd.DataFrame:
    """input: months list: as ints
    stores to results also to results_folder_cum/f'appended_{fileNameSuffix}.csv'
    """
    df_appended = pd.DataFrame()

    for month in months:
        cum_csv_path = get_cum_csv_path(month, subset, results_folder_cum)
        df = fi.df_from_file_or_folder(cum_csv_path)
        df['Month'] = month

        df_appended = pd.concat([df_appended, df])
        df_appended.name = fileNameSuffix
    fi.df_export(df_appended, results_folder_cum/f'appended_{fileNameSuffix}.csv')
    return df_appended


def load_dfs_for_subplots(
        csv_files: list, labels: list, exclue_month=12) -> pd.DataFrame:
    """and filter out edges (posts and outliers due to unrepresentative deep
    shadow next to posts"""

    dfs = pd.DataFrame()
    for i, file in enumerate(csv_files):
        df = fi.df_from_file_or_folder(file)
        print(file)
        df['label'] = labels[i]

        df['custom_index'] = df['xy']+'_M'+df['Month'].astype(str)
        df.set_index('custom_index', inplace=True)
        df = df[df['Month'] != exclue_month]

        # filter posts
        s = 0.25  # 5 pixel a 0.05m #1.25
        x_l, x_r = df['x'].min()+s, df['x'].max()-s
        y_bot, y_up = df['y'].min()+s, df['y'].max()-s
        print('x_length: ', x_r-x_l, 'y_length: ', y_up-y_bot)
        df = df[(df['x'] > x_l) | (df['y'] > y_bot)]  # bot left
        df = df[(df['x'] < x_r) | (df['y'] > y_bot)]  # bot right
        df = df[(df['x'] > x_l) | (df['y'] < y_up)]  # top left
        df = df[(df['x'] < x_r) | (df['y'] < y_up)]  # top right

        # shift x,y min to zero
        df['x'] = df['x']-df['x'].min()
        df['y'] = df['y']-df['y'].min()

        dfs = pd.concat([dfs, df])
    return dfs


# #
