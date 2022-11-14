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
from aiana.classes.aiana_main import AianaMain
from aiana.classes.util_classes.settings_handler import Settings

if __name__ == '__main__':
    settings = Settings()
    settings.sim.study_sub_folderName = 'test7'
    settings.sim.spatial_resolution = 0.5
    settings.sim.hours = list(range(3, 15))  # only morning
    am = AianaMain(settings)

    #am.create_and_view_octfile_for_SceneInspection()
##
if __name__ == '__main__':
    for month in [4, 8]:
        am.update_simTime(month=month)
        am.simulate_and_evaluate(  # skip_sim_for_existing_results=True
        )
# #
