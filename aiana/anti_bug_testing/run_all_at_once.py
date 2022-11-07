# #
import aiana.anti_bug_testing.testing_of_apv_settings as apv_test
import aiana.anti_bug_testing.testing_of_sim_and_view_settings as sim_test
from aiana.utils import files_interface as fi
from aiana.anti_bug_testing.tester_class import Tester

# #
apv_test.run_apv_test(mode='create_reference',
                      # open_oct_viewer=True
                      )
# #
sim_test.run_sim_settings_test(mode='create_reference')
# #
apv_test.run_apv_test()  # default mode='test' and compare to reference
# #
sim_test.run_sim_settings_test()

# #
# results overview bar plot
csv_path = testerObj = Tester().RMSE_MBE_csv_path
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

# #
