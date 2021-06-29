# #
import hjson
from types import SimpleNamespace
from pathlib import Path
import apv
from apv.settings import Simulation
import subprocess
from bifacial_radiance import *
from pvlib import *
import numpy as np
import pandas as pd
import json
import os
import pytictoc
import apv.resources.locations as loc
from apv.settings import Simulation as s
from apv.settings import UserPaths as up
from apv.utils import files_interface as fi
from apv.utils import time
from apv import br_wrapper as br
import importlib as imp
imp.reload(apv)
# #
x = br.setup_br(sky_gen_type='gendaylit', cellLevelModule=False, EPW=True)
# #
print(x)

# !!
print(type(x[2]))
# !!
testfolder = up.root_folder
View_scene = os.path.join(testfolder, 'views', 'overall.vp')
with open(View_scene, 'w') as f:
    f.write('rvu -vtv -vp '              # vp = view port
            + '-15 '                     # X (depth)
            + '-1.8 '                    # Y (left / right)
            + '6 '                       # Z (height)
            + '-vd 1.581 0 -0.519234 '   # vd = view direction
            + '-vu 0 0 1 '               # vu = view "Up" ???
            + '-vh 110 -vv 45 '          # vh/vv = horizonor
            + '-vs 0 -vl 0')             # vs/vl:
br.view_oct_file_with_rvu(view_fp=View_scene, oct_file_name='APV_floating')
# !!

br.ground_simulation(radObj=x[0], scene=x[2], oct_file_name=x[1])

# !!
print(type(s.start_time))


# #

a = 'ab'
s = '2+len(a)'
eval(s)

# #
text = """{
    test: {
        foo: 2
        bar: 1
    }
}"""

data = hjson.loads(text)


# #
str(apv.settings.UserPaths.data_download_folder)

# #

# Parse JSON into an object with attributes corresponding to dict keys.
x = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

# #
d2 = dotdict(d)
d2.test.foo
# 'it works'
# #
mydict.nested = dotdict(nested_dict)
mydict.nested.val
# 'nested works too'

# #
root_folder = (Path().home().resolve() / 'Documents' /
               'Python_Scripts' / 'parameter_study')
p = root_folder / r'Trading\test'
str(p)
