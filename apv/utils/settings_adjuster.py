
from apv.settings import Simulation as simSettingsObj


def adjust_settings(simSettings: simSettingsObj) -> simSettingsObj:

    print('\n##### ' + simSettings.module_form.replace('_', ' ')
          + ' simulation mode #####\n')

    if simSettings.module_form == 'cell_level_checker_board':
        # for checkerboard on cell level calculate only one module
        # and enlarge module in y direction to have the same PV output
        simSettings.moduleDict['y'] *= 2
        simSettings.cellLevelModuleParams['numcellsy'] *= 2
        simSettings.sceneDict['nRows'] = 1
        simSettings.sceneDict['nMods'] = 1

    # add cell sizes

    def _calc_cell_size(mod_size, num_cell, cell_gap):
        # x = numcellsx * xcell + (numcellsx-1)*xcellgap
        # xcell = (x - (numcellsx-1)*xcellgap) / numcellsx
        cell_size = (mod_size - (num_cell-1)*cell_gap) / num_cell
        return cell_size

    simSettings.cellLevelModuleParams['xcell'] = _calc_cell_size(
        simSettings.moduleDict['x'],
        simSettings.cellLevelModuleParams['numcellsx'],
        simSettings.cellLevelModuleParams['xcellgap']
    )

    simSettings.cellLevelModuleParams['ycell'] = _calc_cell_size(
        simSettings.moduleDict['y'],
        simSettings.cellLevelModuleParams['numcellsy'],
        simSettings.cellLevelModuleParams['ycellgap']
    )

    return simSettings
