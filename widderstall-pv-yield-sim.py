##''
import core as core_module
import importlib as imp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# import os as os
# from datetime import datetime as dt
# import time as t
# import json
# from tqdm.auto import trange, tqdm
# import itertools

imp.reload(core_module)
cf = core_module.CoreFunctions()
##''

module_ws = cf.df_from_file('raw-data/Sanyo240_moduleSpecs_guestimate.txt', delimiter='\t').T
module_ws

##''


