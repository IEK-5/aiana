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
from aiana.settings.apv_system_settings import APV_Syst_InclinedTables_S_Morschenich
from aiana.utils.study_utils import adjust_settings_StudyForMorschenich

if __name__ == '__main__':
    settings = Settings()
    settings.apv = APV_Syst_InclinedTables_S_Morschenich()

    settings.sim.study_name = 'APV_Morschenich_2022_IGB2'
    settings.sim.sub_study_name = 'test_run'
    settings.sim.spatial_resolution = 0.5
    settings.sim.time_step_in_minutes = 15
    settings.sim.hours = list(range(12, 13))
    # TODO check anchor y calculation...
    settings = adjust_settings_StudyForMorschenich(settings)

    settings.apv.module_form = 'none'

    am = AianaMain(settings)
    am.create_and_view_octfile_for_SceneInspection(view_name='top_down')
# #
if __name__ == '__main__':
    for month in [4, 8]:
        am.update_simTime_and_resultPaths(month=month)
        am.simulate_and_evaluate(  # skip_sim_for_existing_results=True
        )
# #
