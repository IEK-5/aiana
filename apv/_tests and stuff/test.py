# #
import datetime
import random
import time
import sys
import importlib as imp
from apv import br_wrapper as br
from apv.utils import files_interface as fi
from apv.settings import UserPaths as up
from apv.settings import Simulation as s
import apv.resources.locations as loc
import pytictoc
import os
import json
import pandas as pd
import numpy as np
from pvlib import *
from bifacial_radiance import *
import subprocess
from apv.settings import Simulation
import apv
from pathlib import Path
from types import SimpleNamespace
import hjson
import this
from datetime import datetime

# #


def get_hour_of_year(date_time_str: str) -> int:
    """converts str to hours_of_year

    Args:
        date_time_str (str): format: 'month-day_hour'+'h',
        e.g.'06-15_10h'

    Returns:
        int: hours_of_year
    """
    date_time_obj = datetime.strptime(date_time_str, '%m-%d_%Hh')

    date_time_str_ref = '01-01_00h'
    date_time_obj_ref = datetime.strptime(date_time_str_ref, '%m-%d_%Hh')

    delta = date_time_obj - date_time_obj_ref
    return delta.days * 24 + date_time_obj.hour


get_hour_of_year('06-15_9h')
# #

get_hour_of_year('06-17_12h')
# #
imp.reload(apv)
# #


class Test():
    x = 1

    def __init__(self):
        self.y = 3

    def method(self):
        print(self.x)
        print(self.y)

    @classmethod
    def class_method(cls):
        print(cls.x)

    @staticmethod
    def static_method(string='hi'):
        print(string)


t = Test()
t.x = 2

print('method:')
t.method()
print('class method:')
t.class_method()
print('static method:')
t.static_method()


print('x not changed')
t = Test()
print('method:')
t.method()
print('class method:')
t.class_method()
print('static method:')
t.static_method('hi2')
# #


class Test():
    x = 1

    def method(self):
        print(self.x)

    @classmethod
    def class_method(cls):
        print(cls.x)


t = Test()
t.x = 2
print('method:')
t.method()
print('class method:')
t.class_method()

# #


class Test():
    x = 1

    def __init__(self):
        self.y = 1

    def method(self):
        print(self.x)
        # print(self.y)


t = Test()
t2 = Test()
t2.x = 2
t.method()
Test.x = 3
t.method()
t2.method()


# #

def clear(): return os.system('clear')


for i in range(2):
    for i in range(1, 4):
        clear()
        print('Loading' + "."*i)
        time.sleep(0.5)
# #


class Test():
    x = 1

    def __init__(self):
        self.y = 1

    def method(self):
        print(self.y)
        # print(self.y)


t = Test()
t2 = Test()
t2.y = 2
t.method()
Test.y = 3
t.method()
t2.method()
t3 = Test()
t3.method()
# t2.method()
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
br.view_scene(view_fp=View_scene, oct_file_name='APV_floating')
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
