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
    settings.sim.study_name = 'MyStudy'
    settings.sim.spatial_resolution = 0.5
    settings.sim.time_step_in_minutes = 30
    am = AianaMain(settings)
    am.create_and_view_octfile_for_SceneInspection()
# #
if __name__ == '__main__':
    settings.sim.hours = list(range(10, 15))
    for pitch in [5, 10]:
        settings.apv.sceneDict['pitch'] = pitch
        settings.sim.sub_study_name = f'pitch{pitch}'
        am = AianaMain(settings)  # to spread updated settings to sub classes
        for month in [3, 6]:
            # see sim_settings.py for other default settings such as the day
            # if you want to change only the day or month within a loop,
            # you can re-use the same AianaMain() instance (here ´am´)
            am.update_simTime_and_resultPaths(month=month)
            am.simulate_and_evaluate(  # skip_sim_for_existing_results=True
            )
# #
