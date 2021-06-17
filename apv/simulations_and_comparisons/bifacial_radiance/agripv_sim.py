# #
import bifacial_radiance as br
import numpy as np
import os as os
import importlib as imp
import apv
from pathlib import Path


# #
imp.reload(apv)

credentials = apv.utils.weather_data.load_API_credentials()
location = apv.resources.locations.Morschenich_AgriPV

# #
# Download wind and temperature data
cds_file_name = 'temp_and_wind_data'

apv.utils.weather_data.download_wind_and_T_data(
    credentials,
    file_name=cds_file_name,
    location=location,
    year='2021', month='01', day=['02', '03']
)

# #
df = apv.utils.files_interface.df_from_nc(
    rel_path='data_downloads/'+cds_file_name+'.nc')
df

# #
# Download insolation data
ads_file_name = 'insolation_data'
apv.utils.weather_data.download_insolation_data(
    credentials,
    file_name=ads_file_name,
    location=location,
    date_range='2015-01-01/2015-01-02',
    time_step='1hour')

# #
df = apv.utils.files_interface.df_from_file(
    rel_path='data_downloads/'+ads_file_name+'.csv',
    skiprows=42, delimiter=';')
df  # (BNI = DNI)

# #


result_folder = os.path.join(
    apv.utils.files_interface.path_main,
    'results',
    'bifacial_radiance_tutorials')

# set the time stamp [h/year]  Noon, June 17th.
timestamp = 4020
# name of the .oct file
oct_fn = 'AgriPV'
# an .oct file combines all of the ground, sky and object
# and thus describes the radiance scene

# Location:
site = apv.resources.locations.Morschenich_AgriPV

# TorqueTube Parameters
axisofrotationTorqueTube = False
torqueTube = False
cellLevelModule = True


# Create a RadianceObj 'object'
RadObj = br.RadianceObj(oct_fn, path=result_folder)
# albedo input
RadObj.setGround(0.2)

epwfile = RadObj.getEPW(site.latitude, site.longitude)
# #
RadObj.readEPW(epwfile)
# #

# #
metdata = RadObj.readEPW(epwfile)  # read in the EPW weather data from above
RadObj.gendaylit(timestamp)  # Use this to simulate only one hour at a time.
# This allows you to "view" the scene on RVU (see instructions below)
# RadObj.genCumSky(RadObj.epwfile) # Use this instead of gendaylit to simulate
# the whole year

# Making module with all the variables
moduletype = 'PrismSolar'
numpanels = 2
sensorsy = 6*numpanels  # this will give 6 sensors per module, 1 per cell

moduleDict = RadObj.makeModule(  # if celllevel is defined, x and y aren't needed
    name=moduletype, numpanels=numpanels,
    xgap=0.10, ygap=0.10,
    cellLevelModuleParams=apv.settings.SimGeometries.cellLevelModuleParams)

# makeScene creates a .rad file
scene = RadObj.makeScene(
    moduletype=moduletype, sceneDict=apv.settings.SimGeometries.sceneDict)
# make .oct file
octfile = RadObj.makeOct(RadObj.getfilelist())

# #
# define the view file path
view_fp = os.path.join(result_folder, 'views', 'total.vp')

# write file for viewer (radiance/bin/rvu.exe) with camera settings
with open(view_fp, 'w') as f:
    f.write('rvu -vtv -vp '  # vp = view port
            + '-15 '   # X (depth)
            + '-1.6 '  # Y (left / right)
            + '6 '     # Z (height)
            + '-vd 1.581 0 -0.519234 '  # vd = view direction
            + '-vu 0 0 1 '  # vu = view "Up" ???
            + '-vh 110 -vv 45 '  # vh/vv = horizontal/vertical display size
            + '-vo 0 -va 0 '  # vo/va: clipping plane before/after
            + '-vs 0 -vl 0')  # vs/vl: horizontal/vertical view offset

# view the .oct file with rvu:
# !rvu -vf $view_fp -e .01 AgriPV.oct

# #
# # Adding different Albedo Sections
# Add a surface with a specific reflectivity to represent different
# albedo sections. In the image, we can see that the albedo between
# the crops is different than the crop albedo. Let's assume that
# the abledo between the crops is higher than the crop's albedo
# which was previuosly set a 0.2.

name = 'Center_Grass'
carpositionx = -2
carpositiony = -1
text = '! genbox white_EPDM CenterPatch 28 12 0.1 | xform -t -14 2 0'.format(
    carpositionx, carpositiony)
customObject = RadObj.makeCustomObject(name, text)
RadObj.appendtoScene(scene.radfiles, customObject, '!xform -rz 0')

# makeOct combines all of the ground, sky and object files into a .oct file.
octfile = RadObj.makeOct(RadObj.getfilelist())

# #
# import subprocess


def view_oct_file_with_rvu(view_fp, oct_fn):
    oct_fn_with_ext = oct_fn + '.oct'
    # view the .oct file with rvu:
    !rvu - vf $view_fp - e .01 $oct_fn_with_ext
    # carefull: evgenii said it works only in vs code or jupyter
    # can be solved with the subprocess lib


view_oct_file_with_rvu(view_fp, oct_fn)


# #

# Viewing with rvu:
#
# ![AgriPV modeled step 4](../images_wiki/AdvancedJournals/AgriPV_step4.PNG)
#
#

# <a id='step4'></a>

# ### 4. Analysis of the Ground Irradiance
#
# Now let's do some analysis along the ground, starting from the edge of the
# modules. We wil select to start in the center of the array.
#
# We are also increasign the number of points sampled accross the collector
# width, with the  variable **sensorsy** passed to **moduleanalysis**.
# We are also increasing the step between sampling points,
# to be able to sample in between the rows.

# In[8]:


# return an analysis object including the scan dimensions for back irradiance
analysis = br.AnalysisObj(octfile, RadObj.name)
sensorsy = 20  # je höher desto besser aufgelöst
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)


# In[10]:


groundscan = frontscan


# In[13]:


groundscan['zstart'] = 0.05  # setting it 5 cm from the ground.
groundscan['zinc'] = 0   # no tilt necessary.
groundscan['yinc'] = sceneDict['pitch']/(sensorsy-1)   # no tilt necessary.
groundscan['xinc'] = groundscan['yinc']
groundscan['Nx'] = 2
groundscan


# In[14]:


# compare the back vs front irradiance
analysis.analysis(octfile, oct_fn+"_groundscan", groundscan, backscan)


# In[20]:


analysis.Wm2Front


# # TO ADD: MAP more underneat the module, load results and make colormap.

# <a id='step4'></a>

# <div class="alert alert-warning">
# This is a note.
#
# </div>
#
#

# #

analysis.y


# #
