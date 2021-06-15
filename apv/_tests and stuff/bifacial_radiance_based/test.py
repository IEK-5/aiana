# #
import bifacial_radiance as br
br.gui()
# #
br.gui()

#bifacial_radiance.gui()

# #

import os
from pathlib import Path

testfolder = Path().resolve().parent.parent / 'bifacial_radiance' / 'TEMP'

# Another option using relative address; for some operative systems you might need '/' instead of '\'
# testfolder = os.path.abspath(r'..\..\bifacial_radiance\TEMP')  

print ("Your simulation will be stored in %s" % testfolder)


# #


demo = br.RadianceObj('bifacial_example',str(testfolder))  
module_type = 'Prism Solar Bi60 landscape' 
demo.makeModule(name=module_type,x=1.695, y=0.984)
availableModules = demo.printModules()
sceneDict = {'tilt':10,'pitch':3,'clearance_height':0.2,'azimuth':180, 'nMods': 20, 'nRows': 7} 
scene = demo.makeScene(module_type,sceneDict)
octfile = demo.makeOct(demo.getfilelist())  

analysis = br.AnalysisObj(octfile, demo.basename)
frontscan, backscan = analysis.moduleAnalysis(scene)
br.analysis.analysis(octfile, demo.basename, frontscan, backscan)  

# #
