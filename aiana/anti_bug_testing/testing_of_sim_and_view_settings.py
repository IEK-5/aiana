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
from aiana.anti_bug_testing.tester_class import Tester


def run_sim_settings_test(**kwargs):
    """**kwargs:
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
    testerObj.test_listItems_separately("rtraceAccuracy", [
        'std', 'accurate', 'hq', 'good_no_interp', 'acc_no_interp'])


# #
# view settings
if __name__ == '__main__':
    testerObj = Tester(open_oct_viewer=True)
    testerObj.test_inverted_bool_settings(['use_acceleradRT_view'])
