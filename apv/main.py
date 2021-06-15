# #
import apv
import bifacial_radiance as br

if __name__ == "__main__":
    userPaths = apv.settings.UserPaths()
    simSettings = apv.settings.Simulation()
    print('checking folders')
    paths_list = [userPaths.root_folder,
                  userPaths.radiance_files_folder,
                  userPaths.results_folder,
                  userPaths.data_download_folder]
    apv.tools.files_interface.make_dirs_if_not_there(paths_list)

    print('starting simulation')
    radObj = br.RadianceObj(
        simSettings.name,
        path=userPaths.radiance_files_folder)
    radObj.setGround(simSettings.ground_albedo)
    # EPW data according lat/lon
    epwfile = radObj.getEPW(
        simSettings.apv_location.latitude,
        simSettings.apv_location.longitude)
    # read in the EPW weather data from above
    metdata = radObj.readEPW(epwfile)
    # Use this to simulate only one hour at a time.
    radObj.gendaylit(simSettings.hour_of_year)
    # radObj.genCumSky(radObj.epwfile)   # Can use this instead of gendaylit to simulate the whole year.

# #
    # Making module with all the variables
    moduleDict = radObj.makeModule(
        name=moduletype, x=x, y=y, numpanels=numpanels, xgap=xgap, ygap=ygap,
        cellLevelModuleParams=cellLevelModuleParams)

    # create a scene with all the variables
    sceneDict = {'tilt': tilt, 'pitch': 15, 'hub_height': hub_height,
                 'azimuth': azimuth_ang, 'module_type': moduletype, 'nMods': nMods, 'nRows': nRows}
    scene = radObj.makeScene(
        moduletype=moduletype,
        sceneDict=simSettings.geometries.sceneDict)
    octfile = radObj.makeOct(radObj.getfilelist())

    # In[4]
    # View scene
    View_scene = os.path.join(testfolder, 'views', 'overall.vp')
    with open(View_scene, 'w') as f:
        f.write('rvu -vtv -vp '              # vp = view port
                + '-15 '                     # X (depth)
                + '-1.8 '                    # Y (left / right)
                + '6 '                       # Z (height)
                + '-vd 1.581 0 -0.519234 '   # vd = view direction
                + '-vu 0 0 1 '               # vu = view "Up" ???
                + '-vh 110 -vv 45 '          # vh/vv = horizontal/vertical display size
                + '-vo 0 -va 0 '             # vo/va: clipping plane before/after
                + '-vs 0 -vl 0')             # vs/vl: horizontal/vertical view offset

    !rvu - vf $View_scene - e .01 APV_Floating.oct

    # In[5]:
    # Adding the structure

    #torquetubelength = moduleDict['scenex']*(nMods)
    # torquetube 1
    # name='Post1'
    #text='! genbox Metal_Aluminum_Anodized torquetube_row1 {} 0.2 0.3 | xform -t {} -0.1 -0.3 | xform -t 0 0 4.2'.format(torquetubelength, (-torquetubelength+moduleDict['sceney'])/2.0)
    #text='! genbox black cuteBox 10 0.2 0.3 | xform -t -5 -0.1 -0.15 | xform  -t 0 15 4.2'.format(z2nd, xleft, y2nd)
    #customObject = radObj.makeCustomObject(name,text)
    #radObj.appendtoScene(radfile=scene.radfiles, customObject=customObject, text="!xform -rz 0")
    # name='Post2'
    #text='! genbox Metal_Aluminum_Anodized torquetube_row2 {} 0.2 0.3 | xform -t {} -0.1 -0.3 | xform -t 0 15 4.2'.format(torquetubelength, (-torquetubelength+moduleDict['sceney'])/2.0)
    #customObject = radObj.makeCustomObject(name,text)
    #radObj.appendtoScene(radfile=scene.radfiles, customObject=customObject, text="!xform -rz 0")
    # octfile = radObj.makeOct()  # makeOct combines all of the ground, sky and object files into a .oct file.

    # In[6]:

    # Cont. Structure

    # name='Pile'
    #pile1x = (torquetubelength+moduleDict['sceney'])/2.0
    #pilesep = pile1x*2.0/7.0
    #! genrev Metal_Grey tube1 t*1.004 0.05 32 | xform -ry 90 -t -0.502 0 0
    #text= '! genrev Metal_Grey tube1row1 t*4.2 0.15 32 | xform -t {} 0 0'.format(pile1x)
    #text += '\r\n! genrev Metal_Grey tube1row2 t*4.2 0.15 32 | xform -t {} 15 0'.format(pile1x)
    #
    # for i in range (1, 7):
    #    text += '\r\n! genrev Metal_Grey tube{}row1 t*4.2 0.15 32 | xform -t {} 0 0'.format(i+1, pile1x-pilesep*i)
    #    text += '\r\n! genrev Metal_Grey tube{}row2 t*4.2 0.15 32 | xform -t {} 15 0'.format(i+1, pile1x-pilesep*i)

    #customObject = radObj.makeCustomObject(name,text)
    #radObj.appendtoScene(radfile=scene.radfiles, customObject=customObject, text="!xform -rz 0")

    # octfile = radObj.makeOct()  # makeOct combines all of the ground, sky and object files into a .oct file.
    # In[7]:

    # Adding different Albedo Sections

    # name='Center_Grass'
    # carpositionx=-2
    # carpositiony=-1
    #text='! genbox white_EPDM CenterPatch 28 12 0.1 | xform -t -14 2 0'.format(carpositionx, carpositiony)
    #customObject = radObj.makeCustomObject(name,text)
    #radObj.appendtoScene(scene.radfiles, customObject, '!xform -rz 0')
    # octfile = radObj.makeOct(radObj.getfilelist())  # makeOct combines all of the ground, sky and object files into a .oct file.
    # In[8]:
    # Analysis of the Ground Irradiance
    # return an analysis object including the scan dimensions for back irradiance
    analysis = AnalysisObj(octfile, radObj.name)
    sensorsy = 21  # number of sensors along y-axis
    frontscan, backscan = analysis.moduleAnalysis(scene, sensorsy=sensorsy,
                                                  modWanted=30, rowWanted=3)
    results = analysis.analysis(octfile, radObj.basename, frontscan, backscan)
    print('Checking results...')
    load.read1Result(os.path.join(testfolder, 'results\irr_{}.csv'.format(simulationname)))

    # In[9]:
    # define ground to manipulate sensor locations on ground
    groundscan = frontscan
    groundscan
    # In[10]:
    # Locating sensors on ground
    groundscan['ystart'] = -12.97
    ygrid = np.arange(-12.97, 12.97, 1.297)

    groundscan['xstart'] = -5.38
    groundscan['xinc'] = 0.538

    groundscan['zstart'] = 0.05  # setting it 5 cm from the ground.
    groundscan['zinc'] = 0       # no tilt necessary.

    groundscan

    # In[11]:
    # Analysis and Results on ground
    for i in ygrid:
        groundscan['ystart'] = i
        groundscan['yinc'] = 0   # no tilt necessary.
        analysis.analysis(octfile, simulationname+"_groundscan"+'%.3f' %
                          i, groundscan, backscan, accuracy='low')

    # In[12]:
    # check ground grid
    # print('Results on ground at z= 0.05 y= 0 and along the x-axis \n')
    # r_ground = load.read1Result(os.path.join(testfolder\
    #     ,'results\irr_{}_groundscan0.000.csv'.format(simulationname)))
    # r_ground
    # In[13]
    # Merge results to create one complete ground DataFrame
    dfs = []
    for i in np.arange(-12.970, 12.970, 1.297):
        print('reading...results\irr_{}_groundscan{:.3f}.csv'.format(simulationname, i))

        file_to_add = load.read1Result(os.path.join(
            testfolder, 'results\irr_{}_groundscan{:.3f}.csv'.format(simulationname, i)))
        dfs.append(file_to_add)
    groundscan = pd.concat(dfs)
    groundscan = groundscan.reset_index()
    groundscan = groundscan.rename(columns={'Wm2Front': 'Wm2Ground'})
    groundscan.tail()

    # In[14]
    # Draw heat map of ground radiation

    def plot_heatmap(df: pd.DataFrame, x: str, y: str, z: str):
        f, ax = plt.subplots(1, 1, figsize=(8, 4))
        data = df.pivot(y, x, z)
        print(data)
        cm = 'inferno'
        ax = sns.heatmap(data, annot=False, linewidths=0, ax=ax, cmap=cm, cbar_kws={'label': z})
        ax.invert_yaxis()
        xlabels = ['{:.2f}'.format(float(item.get_text()))
                   for item in ax.get_xticklabels()]

        ax.set_xticklabels(xlabels)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    plot_heatmap(groundscan, 'x', 'y', 'Wm2Ground')


# #
apv.settings.UserPaths.__name__
# #
userPaths.__class__.__name__
