""" This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>."""
# #

from pvlib import location
from aiana.anti_bug_testing.tester_class import Tester


def run_sim_settings_test(**kwargs):
    """
    The sim settings attributes 'study_name', 'sub_study_name' '
    are changed during the test anyway.

    NOTE for parallelization == 'None' also other settings are changed
    (resolution, hours... to reduce sim duration)


    **kwargs:
        mode (optional): Defaults to 'test'
        (which means 1. simulate 2. check and plot difference to reference)
            alternative: 'create_reference'

        open_oct_viewer (bool, optional): to check scene creation for each set.
        Viewer needs to be closed manualy. Defaults to False.

        default_settings (Settings, optional): Defaults to None (constructing
            automatically based on setting files)

        run_simulation (bool, optional): Defaults to True, can be set False,
            if only viewing is of interest.
    """
    testerObj = Tester(**kwargs)
    testerObj.test_listItems_separately("spatial_resolution", [0.5, 0.2])
    testerObj.test_listItems_separately("ground_albedo", [0.05, 0.5])

    # #
    #testerObj = Tester(run_simulation=False, open_oct_viewer=True)
    testerObj.test_listItems_separately(
        "hour_for_sceneInspection", [8, 10, 16])
    # #
    testerObj.test_listItems_separately("year", [2020])
    testerObj.test_listItems_separately("month", [3])
    testerObj.test_listItems_separately("day", [1])

    # to reduce sim duration without GPU and to test hours and temporal
    # resolution (time_step_in_minutes), change default settings, to which
    # test_listItems_separately will fall back after each tested listItem:
    testerObj.default_settings.sim.hours = [14]
    testerObj.default_settings.sim.time_step_in_minutes = 60
    testerObj.default_settings.sim.spatial_resolution = 0.2
    testerObj.test_listItems_separately("parallelization", [
        'None',
        # 'multiCore', not working at the moment
        #  'GPU' # (standard)
    ])
    # #
    # reset
    testerObj = Tester(**kwargs)
    # #
    # testerObj = Tester(mode='create_reference')
    testerObj.test_listItems_separately("aggregate_irradiance_perTimeOfDay", [
        'False', 'over_the_week', 'over_the_month'
    ])
    testerObj.test_listItems_separately("irradiance_aggfunc", ['min', 'max'])

    testerObj.test_listItems_separately("rtraceAccuracy", [
        'std', 'accurate', 'hq', 'good_no_interp', 'acc_no_interp'])

    # #
    #from aiana.anti_bug_testing.tester_class import Tester
    #testerObj = Tester(mode='create_reference')
    # to test and to shorten test weather data size
    testerObj.settings.sim.date_range_to_calc_TMY = '2022-01-01/2022-12-31'
    testerObj.settings.sim.apv_location = location.Location(
        48.533, 9.717, altitude=750, tz='Europe/Berlin', name='Widderstall')
    testerObj.test_with_current_settings_then_reset_to_DefaultSettings(
        'location-Widderstall')


# #
# view settings
if __name__ == '__main__':
    from aiana.anti_bug_testing.tester_class import Tester
    testerObj = Tester(open_oct_viewer=True, run_simulation=False,
                       mode='create_reference')
    testerObj.test_listItems_separately('accelerad_img_height', [400])
    # #
    testerObj.test_inverted_bool_settings(['use_acceleradRT_view'])
