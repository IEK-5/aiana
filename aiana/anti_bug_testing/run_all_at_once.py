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
import os
import aiana.anti_bug_testing.testing_of_apv_settings as apv_test
import aiana.anti_bug_testing.testing_of_sim_and_view_settings as sim_test
from aiana.utils import files_interface as fi
from aiana.anti_bug_testing.tester_class import Tester

# #
# optionally delete previous test results from
csv_path = Tester().RMSE_MBE_csv_path
os.remove(csv_path)

# #
# optionally create new apv system settings reference
# remark: if you do this, you should check all results manualy again, also with
# open_oct_viewer=True. If you just want to test for bugs due to code changes,
# skip this.
apv_test.run_apv_test(mode='create_reference',
                      # open_oct_viewer=True
                      )
# #
# optionally create new sim settings reference, remark as above
sim_test.run_sim_settings_test(mode='create_reference')  
# #
apv_test.run_apv_test()  # default mode='test' to compare to reference
# #
sim_test.run_sim_settings_test()

# #
# results overview bar plot
csv_path = Tester().RMSE_MBE_csv_path
df = fi.df_from_file_or_folder(csv_path, index_col=0)
df
# #
del df['MBE'], df['RMSE']
df.sort_index(inplace=True, ascending=False)
ax = df.plot(kind='barh', figsize=(8, 0.5*len(df)), width=1)
ax.grid()
for container in ax.containers:
    ax.bar_label(container, padding=5, fmt='%.2g',
                 label_type='center')
ax.get_figure().savefig(csv_path.parents[1]/'dif_overview.jpg',
                        bbox_inches='tight', dpi=300)
# NOTE  higher relRMSE for different rtrace accuracy settings is normal due to
# interpolation artefacts near the post
# #
