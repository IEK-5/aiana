from apv.settings.apv_systems import Default as APV_SystSettingsObj


def adjust_settings(
    APV_SystSettings: APV_SystSettingsObj
) -> APV_SystSettingsObj:

    print('\n##### ' + APV_SystSettings.module_form.replace('_', ' ')
          + ' simulation mode #####\n')

    # if simSettings.module_form == 'cell_level_checker_board':
    #     # for checkerboard on cell level calculate only one module
    #     # and enlarge module in y direction to have the same PV output
    #     # TODO ??
    #     simSettings.moduleDict['y'] *= 2
    #     simSettings.cellLevelModuleParams['numcellsy'] *= 2
    #     simSettings.sceneDict['nRows'] = 1
    #     simSettings.sceneDict['nMods'] = 5
    if APV_SystSettings.module_form == 'EW_fixed' or \
            APV_SystSettings.module_form == 'cell_level_EW_fixed':
        APV_SystSettings.sceneDict['azimuth'] == 90
        APV_SystSettings.moduleDict['numpanels'] == 2
    # add cell sizes

    def _calc_cell_size(mod_size, num_cell, cell_gap):
        # x = numcellsx * xcell + (numcellsx-1)*xcellgap
        # xcell = (x - (numcellsx-1)*xcellgap) / numcellsx
        cell_size = (mod_size - (num_cell-1)*cell_gap) / num_cell
        return cell_size

    APV_SystSettings.cellLevelModuleParams['xcell'] = _calc_cell_size(
        APV_SystSettings.moduleDict['x'],
        APV_SystSettings.cellLevelModuleParams['numcellsx'],
        APV_SystSettings.cellLevelModuleParams['xcellgap']
    )

    APV_SystSettings.cellLevelModuleParams['ycell'] = _calc_cell_size(
        APV_SystSettings.moduleDict['y'],
        APV_SystSettings.cellLevelModuleParams['numcellsy'],
        APV_SystSettings.cellLevelModuleParams['ycellgap']
    )

    if APV_SystSettings.module_form == 'EW_fixed' or \
            APV_SystSettings.module_form == 'cell_level_EW_fixed':
        APV_SystSettings.sceneDict['azimuth'] == 90
        APV_SystSettings.moduleDict['numpanels'] == 2

    return APV_SystSettings
