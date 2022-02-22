from apv.settings.apv_systems import Default as SystSettings
import numpy as np

# TODO implement into geometries handler


def adjust_apvSystem_settings(
    APV_SystSettings: SystSettings
) -> SystSettings:

    print('\n##### ' + APV_SystSettings.module_form.replace('_', ' ')
          + ' simulation mode #####\n')

    # if simSettings.module_form == 'cell_level_checker_board':
    #     # for checkerboard on cell level calculate only one module
    #     # and enlarge module in y direction to have the same PV output
    #     simSettings.moduleDict['y'] *= 2
    c = APV_SystSettings.cellLevelModuleParams
    x = APV_SystSettings.moduleDict['x']
    y = APV_SystSettings.moduleDict['y']
    mod_form = APV_SystSettings.module_form

    if mod_form == 'EW_fixed' or mod_form == 'cell_level_EW_fixed':
        APV_SystSettings.sceneDict['azimuth'] = 90
        APV_SystSettings.moduleDict['numpanels'] = 2

    c['xcell'] = calc_cell_size(x, c['numcellsx'], c['xcellgap'])
    c['ycell'] = calc_cell_size(y, c['numcellsy'], c['ycellgap'])

    if mod_form in ['cell_level', 'cell_level_EW_fixed',
                    'cell_level_checker_board']:
        if mod_form == 'cell_level_checker_board':
            factor = 2
        else:
            factor = 1
        packingfactor = np.round(
            c['xcell']*c['ycell']*c['numcellsx']*c['numcellsy']/(
                factor*x*y), 2
        )
        print("This is a Cell-Level detailed module with Packaging "
              + f"Factor of {packingfactor}.")

    return APV_SystSettings


def calc_cell_size(mod_size, num_cell, cell_gap):
    # add cell sizes

    # formula derivation:
    # x = numcellsx * xcell + (numcellsx-1) * xcellgap
    # xcell = (x - (numcellsx-1)*xcellgap) / numcellsx
    cell_size = (mod_size - (num_cell-1)*cell_gap) / num_cell
    return cell_size
