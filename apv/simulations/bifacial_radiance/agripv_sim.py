# #
import bifacial_radiance as br
import numpy as np
import os as os
import importlib as imp


import apv.resources
import apv.tools
imp.reload(apv.resources.locations)

# #
result_folder = os.path.join(
    apv.tools.files_interface.path_main,
    'results',
    'bifacial_radiance_tutorials')

timestamp = 4020  # Noon, June 17th.
simulationname = 'AgriPV'

# Location:
site = apv.resources.locations.Morschenich_AgriPV


# TorqueTube Parameters
axisofrotationTorqueTube = False
torqueTube = False
cellLevelModule = True

# x und y vertauschen???
cellLevelModuleParams = {'numcellsx': 6, 'numcellsy': 12,
                         'xcell': 0.156, 'ycell': 0.156,
                         'xcellgap': 0.02, 'ycellgap': 0.02}


# Now let's run the example

# Create a RadianceObj 'object'
demo = br.RadianceObj(simulationname, path=result_folder)
# input albedo number or material name like 'concrete'.  To see options, run this without any input.

demo.setGround(0.2)

# NJ lat/lon 40.0583° N, 74.4057
epwfile = demo.getEPW(site.latitude, site.longitude)
metdata = demo.readEPW(epwfile)  # read in the EPW weather data from above
demo.gendaylit(4020)  # Use this to simulate only one hour at a time.
# This allows you to "view" the scene on RVU (see instructions below)
# timestam 4020 : Noon, June 17th.
# demo.genCumSky(demo.epwfile) # Use this instead of gendaylit to simulate the whole year

moduletype = 'PrismSolar'
# Making module with all the variables

numpanels = 2
x = 0.95
y = 1.95
xgap = 2.0  # Leaving 15 centimeters between modules on x direction
ygap = 0.10  # Leaving 10 centimeters between modules on y direction.
sensorsy = 6*numpanels  # this will give 6 sensors per module, 1 per cell

moduleDict = demo.makeModule(name=moduletype, x=x, y=y, numpanels=numpanels,
                             xgap=0.10, ygap=0.10,
                             cellLevelModuleParams=cellLevelModuleParams)

# all units are in [m] for distances and in [degree] for angles (tilt, azimuth)
sceneDict = {'tilt': 20,
             'pitch': 10,        # distance between two adjacent rows
             'hub_height': 4.5,  # vert. distance: ground to modules
             'azimuth': 180,
             'nMods': 10,        # modules per row
             'nRows': 3}


# makeScene creates a .rad file with 20 modules per row, 7 rows.
scene = demo.makeScene(moduletype=moduletype, sceneDict=sceneDict)
# makeOct combines all of the ground, sky and object fil|es into a .oct file.
octfile = demo.makeOct(demo.getfilelist())

# #
view_fp = os.path.join(result_folder, 'views', 'total.vp')

# object moves to...
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

!rvu -vf $view_fp -e .01 AgriPV.oct

# #


# #
# If you view the Oct file at this point:
#
# ###    rvu -vf views\front.vp -e .01 AgriPV.oct
#
# And adjust the view parameters, you should see this image.
#
# ![AgriPV modeled step 1](../images_wiki/AdvancedJournals/AgriPV_step1.PNG)
#

# <a id='step2'></a>

# ### 2. Adding the structure
#
# We will add on the torquetube and pillars.
#
# Positions of the piles could be done more programatically, but they are kinda estimated at the moment.

# In[5]:


torquetubelength = moduleDict['scenex']*sceneDict['nMods']

# torquetube 1
name = 'Post1'
text = '! genbox Metal_Aluminum_Anodized torquetube_row1 {} 0.2 0.3 | xform -t {} -0.1 -0.3 | xform -t 0 0 4.2'.format(
    torquetubelength, (-torquetubelength+moduleDict['sceney'])/2.0)
# text='! genbox black cuteBox 10 0.2 0.3 | xform -t -5 -0.1 -0.15 | xform  -t 0 15 4.2'.format(z2nd, xleft, y2nd)
customObject = demo.makeCustomObject(name, text)
demo.appendtoScene(radfile=scene.radfiles,
                   customObject=customObject, text="!xform -rz 0")

name = 'Post2'
text = '! genbox Metal_Aluminum_Anodized torquetube_row2 {} 0.2 0.3 | xform -t {} -0.1 -0.3 | xform -t 0 15 4.2'.format(
    torquetubelength, (-torquetubelength+moduleDict['sceney'])/2.0)
customObject = demo.makeCustomObject(name, text)
demo.appendtoScene(radfile=scene.radfiles,
                   customObject=customObject, text="!xform -rz 0")

# octfile = demo.makeOct()  # makeOct combines all of the ground, sky and object files into a .oct file.


# In[6]:


name = 'Pile'
pile1x = (torquetubelength+moduleDict['sceney'])/2.0
pilesep = pile1x*2.0/7.0
# ! genrev Metal_Grey tube1 t*1.004 0.05 32 | xform -ry 90 -t -0.502 0 0
text = '! genrev Metal_Grey tube1row1 t*4.2 0.15 32 | xform -t {} 0 0'.format(
    pile1x)
text += '\r\n! genrev Metal_Grey tube1row2 t*4.2 0.15 32 | xform -t {} 15 0'.format(
    pile1x)

for i in range(1, 7):
    text += '\r\n! genrev Metal_Grey tube{}row1 t*4.2 0.15 32 | xform -t {} 0 0'.format(
        i+1, pile1x-pilesep*i)
    text += '\r\n! genrev Metal_Grey tube{}row2 t*4.2 0.15 32 | xform -t {} 15 0'.format(
        i+1, pile1x-pilesep*i)

customObject = demo.makeCustomObject(name, text)
demo.appendtoScene(radfile=scene.radfiles,
                   customObject=customObject, text="!xform -rz 0")

# makeOct combines all of the ground, sky and object files into a .oct file.
octfile = demo.makeOct()


# ### View the geometry with the posts on :
#
# #### rvu -vf views\front.vp -e .01 -pe 0.4 -vp 12 -10 3.5 -vd -0.0995 0.9950 0.0 AgriPV.oct
#
# ![AgriPV modeled step 2](../images_wiki/AdvancedJournals/AgriPV_step2.PNG)
#

# <a id='step3'></a>
#

# <a id='step3'></a>

# ### 3. Adding different Albedo Sections
# Add a surface (just like we added the pillars) with a specific reflectivity to represent different albedo sections. In the image, we can see that the albedo between the crops is different than the crop albedo. Let's assume that the abledo between the crops is higher than the crop's albedo which wa previuosly set a 0.2.
#
#

# In[16]:


name = 'Center_Grass'
carpositionx = -2
carpositiony = -1
text = '! genbox white_EPDM CenterPatch 28 12 0.1 | xform -t -14 2 0'.format(
    carpositionx, carpositiony)
customObject = demo.makeCustomObject(name, text)
demo.appendtoScene(scene.radfiles, customObject, '!xform -rz 0')

# makeOct combines all of the ground, sky and object files into a .oct file.
octfile = demo.makeOct(demo.getfilelist())


# Viewing with rvu:
#
# ![AgriPV modeled step 4](../images_wiki/AdvancedJournals/AgriPV_step4.PNG)
#
#

# <a id='step4'></a>

# ### 4. Analysis of the Ground Irradiance
#
# Now let's do some analysis along the ground, starting from the edge of the modules. We wil select to start in the center of the array.
#
# We are also increasign the number of points sampled accross the collector width, with the  variable **sensorsy** passed to **moduleanalysis**. We are also increasing the step between sampling points, to be able to sample in between the rows.

# In[8]:


# return an analysis object including the scan dimensions for back irradiance
analysis = br.AnalysisObj(octfile, demo.name)
sensorsy = 20
frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy)


# In[10]:


groundscan = frontscan


# In[13]:


groundscan['zstart'] = 0.05  # setting it 5 cm from the ground.
groundscan['zinc'] = 0   # no tilt necessary.
groundscan['yinc'] = sceneDict['pitch']/(sensorsy-1)   # no tilt necessary.
groundscan


# In[14]:


# compare the back vs front irradiance
analysis.analysis(octfile, simulationname+"_groundscan", groundscan, backscan)


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
