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
import pandas as pd
from aiana.classes.aiana_main import AianaMain
from aiana.classes.util_classes.settings_handler import Settings
from aiana.settings.apv_system_settings import APV_Syst_InclinedTables_S_Morschenich
from aiana.utils.study_utils import adjust_settings_StudyForMorschenich

if __name__ == '__main__':
    settings = Settings()
    settings.apv = APV_Syst_InclinedTables_S_Morschenich()

    settings.apv.glass_modules = False
    # TODO with true, "fatal SUNFARMING0.rad is empty" error
    # probably due to more than one lines in file?

    # TODO height anpassen

    settings.sim.study_name = 'APV_Morschenich_2022_IGB2'
    settings.sim.spatial_resolution = 0.1
    settings.sim.time_step_in_minutes = 10
    settings.sim.year = 2022
    start_month = 3
    start_day = 31  # Thursday
    settings.sim.day = start_day
    settings.sim.month = start_month
    settings.sim.plot_dpi = 100

    settings.sim.aggregate_irradiance_perTimeOfDay = 'over_the_week'
    settings.sim.hours = list(range(12, 13))
    settings.sim.hours = list(range(2, 23))
    settings = adjust_settings_StudyForMorschenich(settings)
    #settings.apv.module_form = 'none'
    am = AianaMain(settings)
    # am.create_and_view_octfile_for_SceneInspection(
    # view_name='top_down', add_NorthArrow=False
    # )

# #
# exp start = thuesday 19.4.,  doing simulations at Thursdays as requested
# (middle of calendar weeks)
# doing april completly so 3+15+3 = 18 weeks in total starting 3 weeks before
# first harvest and skipping week afterfinal harvest #TODO letzten monat auch komplett

if __name__ == '__main__':

    for week_shift in range(18):
        am.update_simTime_and_resultPaths(
            month=start_month, day=start_day)  # reset
        current_timestamp = pd.to_datetime(am.settings._dt.sim_dt_utc) \
            + pd.Timedelta(f'{7*week_shift}day')
        day = current_timestamp.day
        month = current_timestamp.month
        am.update_simTime_and_resultPaths(month=month, day=day)
        KW = am.settings._dt.week
        am.settings.sim.sub_study_name = f'KW{KW}'
        print(day, month, f'KW: {KW}, week_shift: {week_shift}')
        am.simulate_and_evaluate(skip_sim_for_existing_results=True
                                 )


# #
