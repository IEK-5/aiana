''' Called by main.py with the needed parameters to set the neccessary
objects, create scene and run simulation with Bifacial_Radiance according
to presets in settings.py
'''
# import needed packages
from apv.utils import files_interface as fi
from bifacial_radiance.main import RadianceObj
import subprocess
import bifacial_radiance as br
from pvlib import *
import numpy as np
import pandas as pd
import json
import os
import pytictoc
from pathlib import Path

from apv.settings import Simulation as s
from apv.settings import UserPaths

# read simulation settings
moduleDict = s.geometries.moduleDict
sceneDict = s.geometries.sceneDict


def setup_br(sky_gen_type='gendaylit',
             cellLevelModule=False,
             EPW=True):
    """Creates the scene according to parameters and presets defined in
    settings.py - scene created as follows:
    1- create Radiance-Object
    2- setting albedo of ground
    3- read TMY data (from EPW or pre-installed)
    4- create module (either cell defined or not)
    5- create structure object
    5- define number of panels, rows, and columns and final scene (.oct)

    Args:
        sim_type (str, optional): 'gendaylit' for hourly analysis
        or 'gencumsky' for annual perez model --> wird perez model
        nicht auch für gendaylit benutzt?

        cellLevelModule (bool, optional):
        assign module acccording to cell level parameters if true.

        EPW (bool, optional):
        True: downloads nearest EPW data
        False: checks downloaded TMY data.

    Returns:
        radObj: Radiance Object
        scene:
        metdata: Meteorological csv data
    """

    working_folder = UserPaths.bifacial_radiance_files_folder
    # check working folder
    fi.make_dirs_if_not_there(working_folder)

    # create Bifacial_Radiance Object with ground
    radObj = br.RadianceObj(s.name, path=str(working_folder))
    radObj.setGround(s.ground_albedo)

    # read TMY or EPW data
    if EPW is True:
        epw_file = radObj.getEPW(
            lat=s.apv_location.latitude,
            lon=s.apv_location.longitude)
        met_data = radObj.readEPW(epw_file)
    # else:
        # tmy_file = UserPaths.data_download_folder / ...
        # met_data = radObj.readWeatherFile(weatherFile=tmy_file)

    # read and create PV module
    if cellLevelModule is True:
        with open('configs\apv_morschenich.json') as f:
            configs = json.load(f)
            cellLevelModuleParams = configs['cellLevelModuleParams']
            print(cellLevelModuleParams)
            radObj.makeModule(name=s.module_name,
                              **moduleDict,
                              cellLevelModuleParams=cellLevelModuleParams)

    else:
        radObj.makeModule(name=s.module_name,
                          x=moduleDict['x'],
                          y=moduleDict['y'],)

    # create structure <To BE DEFINED LATER>

    # Create Sky
    if sky_gen_type == 'gendaylit':
        if s.start_time == '' and s.end_time == '':
            radObj.gendaylit(timeindex=int(s.hour_of_year))
            oct_file_name = radObj.name + '_{}'.format(s.hour_of_year)
            scene = radObj.makeScene(moduletype=s.module_name,
                                     sceneDict=sceneDict)
            radObj.makeOct(radObj.getfilelist(),
                           octname=oct_file_name)
        else:
            begin = int(s.start_time)
            end = int(s.end_time) + 1
            for timeindex in np.arange(begin, end, 1):
                dni = met_data.dni[timeindex]
                dhi = met_data.dhi[timeindex]
                solpos = met_data.solpos.iloc[timeindex]  # solar position
                sunalt = float(solpos.elevation)
                sunaz = float(solpos.azimuth)
                print(timeindex)
                oct_file_name = radObj.name + '_{}'.format(timeindex)
                sky = radObj.gendaylit2manual(dni, dhi, sunalt, sunaz)
                radObj.makeOct(octname=oct_file_name)

    elif sky_gen_type == 'gencumsky':
        radObj.genCumSky(epwfile=epw_file)
        scene = radObj.makeScene(moduletype=s.module_name,
                                 sceneDict=sceneDict)
        radObj.makeOct(radObj.getfilelist())  # bitte mehr kommentieren

    return radObj, scene, oct_file_name, met_data


def view_scene(view_name: str, oct_file_name=s.name):
    """views an .oct file via radiance/bin/rvu.exe

    Args:
        view_name (str): select from ['total', ...]
        as defined in settings.scene_camera_dicts
        a .vp file will be stored with this name in
        e.g. 'C:\\Users\\Username\\agri-PV\\views\\total.vp'

        oct_fn (str): file name of the .oct file without extension being
        located in the view_fp parent directory (e.g. 'Demo1')
        Defaults to settings.Simulation.name.
    """
    scd = s.scene_camera_dicts[view_name]

    for key in scd:
        scd[key] = str(scd[key])+' '

    view_fp = UserPaths.bifacial_radiance_files_folder / Path(
        'views/'+view_name+'.vp')

    with open(view_fp, 'w') as f:
        f.write(
            'rvu -vtv -vp '
            + scd['cam_pos_x']
            + scd['cam_pos_y']
            + scd['cam_pos_z']
            + '-vd '
            + scd['view_direction_x']
            + scd['view_direction_y']
            + scd['view_direction_z']
            + '-vu 0 0 1 '
            + '-vh '
            + scd['horizontal_view_angle']
            + '- vv '
            + scd['vertical_view_angle']
            + '-vs 0 -vl 0'
        )

    subprocess.call(['rvu', '-vf', view_fp, '-e', '.01', oct_file_name+'.oct'])


def calc_x_field():
    """calulate x_field

    Returns:
        x_field: lengths of the groundsacn area in x direction
        according to scene + 2 m each side
    """
    return round(sceneDict['nMods'] * moduleDict['x']) + 2*2


def calc_y_field() -> int:
    """y_field: lengths of the groundscan area in y direction
    """
    # calulate the footprint of the APV according to the scene + 2 m each side
    y_field = round(
        sceneDict['pitch'] * sceneDict['nRows']
        + moduleDict['y'] * moduleDict['numpanels']
        + 2*2
    )
    return y_field


def get_ygrid():
    y_field = calc_y_field()
    ygrid = np.arange(-y_field / 2, (y_field / 2) + 1, s.spatial_resolution)
    return ygrid


def set_groundscan(groundscan: dict) -> dict:
    """Modifies the groundscan dictionary, except for 'ystart',
    which is set later by looping through ygrid.

    Args:
        groundscan (dict): dictionary containing the XYZ-start and
        -increments values for a bifacial_radiance linescan.
        It describes where the virtual ray tracing sensors are placed.
        The origin (x=0, y=0) of the PV facility is in its center.

    Returns:
        groundscan (dict)
    """
    groundscan['xstart'] = - calc_x_field() / 2
    groundscan['xinc'] = s.spatial_resolution
    groundscan['zstart'] = 0.05
    groundscan['zinc'] = 0
    groundscan['yinc'] = 0

    return groundscan

# class Simulator():


def ground_simulation(radObj: br.RadianceObj,
                      scene: br.SceneObj,
                      oct_file_name: str,
                      accuracy: str):
    """provides irradiation readings on ground in form of a Dataframe
       as per predefined resolution.

    Args:
        radObj (bifacial_radiance.RadianceObj):
        radiance Object, retrieved from running setup_br().

        scene: (bifacial_radiance.SceneObj):

        oct_fn (str): .oct file name with or without extension

        accuracy (str): 'high' or 'low'

    Returns:
        [type]: [description]
    """

    # add extension if not there:
    if oct_file_name[-4] != '.oct':
        oct_file_name += '.oct'

    # instantiate analysis
    analysis = br.AnalysisObj(octfile=oct_file_name, name=radObj.name)

    # ersetzen durch self. ...
    x_field = calc_x_field()

    # number of sensors on ground against y-axis (along x-axis)
    sensorsy = x_field / s.spatial_resolution
    if (sensorsy % 2) == 0:
        sensorsy += 1

    # start rough scan to define ground afterwards
    groundscan, backscan = analysis.moduleAnalysis(scene=scene,
                                                   sensorsy=sensorsy)

    groundscan = set_groundscan(groundscan)
    ygrid = get_ygrid()

    print('\n number of sensor points is {:.0f}'.format((sensorsy*len(ygrid))))
    # Analysis and Results on ground - Time elapsed for analysis shown
    tictoc = pytictoc.TicToc()
    tictoc.tic()
    # simulation time-stamp from settings

    '''
    if s.start_time and s.end_time != '':
        try:
            begin = int(s.start_time)
            end = int(s.end_time) + 1
        except ValueError:
            print('begin and end time must be integers between 0 and 8760')

    else:
        begin = int(s.hour_of_year)
        end = begin + 1
    '''

    # for timeindex in np.arange(begin, end, 1):
    # oct_file_name = radObj.name + '_{}'.format(timeindex)
    for i in ygrid:
        groundscan['ystart'] = i
        temp_name = radObj.name + "_groundscan" + '{:.3f}'.format(i)

        analysis.analysis(oct_file_name,
                          temp_name,
                          groundscan,
                          backscan,
                          accuracy=accuracy)
    tictoc.toc()


def merge_linescans(ygrid, radObj):
    """achtung! geht bisher nur für 'gendaylit'
    wegen timeindex=s.hour_of_year
    für file name. Werde später filesinterface "append all in folder"
    benutzen, dann hat sich das problem von selbst erledigt.
    """
    # Merge results to create one complete ground DataFrame
    dfs = []
    fi.make_dirs_if_not_there(UserPaths.results_folder)

    for i in ygrid:
        print('reading...\n results\\irr_{}_groundscan{:.3f}.csv'
              .format(radObj.name, i))

        file_to_add = br.load.read1Result(os.path.join(
            UserPaths.bifacial_radiance_files_folder,
            'results\\irr_{}_groundscan{:.3f}.csv'
            .format(radObj.name, i)))
        dfs.append(file_to_add)
    print('merging files...')
    groundscan = pd.concat(dfs)
    groundscan = groundscan.reset_index()
    groundscan = groundscan.rename(columns={'Wm2Front': 'Wm2Ground'})
    csv_file_name = 'ground_merged_{}.csv'.format(s.hour_of_year)
    groundscan.to_csv(csv_file_name)
    print('merged file saved as csv file in\
        {} !'.format(UserPaths.results_folder))
    # print('the tail of the data frame shows number of grid \
    #    points \n' + groundscan.tail())

    final_ground = br.load.read1Result(csv_file_name)

    return final_ground
