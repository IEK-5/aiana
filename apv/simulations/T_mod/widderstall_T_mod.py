# #
from pvlib import temperature
import apv.tools

pv_module = apv.tools.files_interface.df_from_file(
    'raw-data/Sanyo240_moduleSpecs_guestimate.txt', delimiter='\t')

df = apv.tools.files_interface.df_from_file(
    'raw-data/sanyo', skiprows=9, append_all_in_folder=True, delimiter='\t')

# labels for x and y to be used in the comparison plot
x = 'experimental $T_{mod}$ [°C]'
df.rename(columns={'Tmod': x}, inplace=True)
y = 'simulated $T_{mod}$ [°C]'

# pv module temperature simulation

df[y] = temperature.sapm_module(
    df['POA'], df['TAA'], df['VW'],
    pv_module['A'][0], pv_module['B'][0]  # glass/polymer, open rack
    )

df[y] = temperature.sapm_cell(
    df['POA'], df['TAA'], df['VW'],
    pv_module['A'][0], pv_module['B'][0], pv_module['DTC'][0]
    )

df.head()
# #
# plotting
import importlib as imp
imp.reload(apv.tools.plots)
apv.tools.files_interface.save_fig(
    apv.tools.plots.comparing_plot_sns(df, x, y, '°C', xy_max=55),
    file_name='Widderstall_Tmod_sim', rel_path='results', dpi=500)
# #
#test
