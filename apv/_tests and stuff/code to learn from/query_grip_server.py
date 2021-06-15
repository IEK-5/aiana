# #
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 09:54:23 2021

@author: neelpatel
"""

import requests
import json
import apv.resources

# #
loc = apv.resources.locations.Jülich_Brainergy
loc.latitude
#%% use when connected to the FZJ VPN

# to get shadow data
shadow_url = 'http://ipv357.ipv.kfa-juelich.de:8080/api/shadow'

# to get server status
status_url = 'http://ipv357.ipv.kfa-juelich.de:8080/api/status'

# get server status

status = requests.get(status_url)
json.loads(status.text)

#%% get shadow data


#bounding_box = [lat_max, lon_max, lat_min, lon_min]  # replace with your lat/lon values

bounding_box = [
        loc.latitude+0.1, loc.longitude+0.1,  # max
        loc.latitude, loc.longitude]          # min


timestr = '2019-11-27_12:00:00'  # replace with your timestring

shadow_params = {'box': bounding_box, 'data_re': '.*_Las.*', 
                     'step': '0.6', 'mesh_type': 'metric', 
                     'output_type': 'geotiff', 'stat': 'max', 
                     'what': 'shadow', 'timestr': timestr}
    
shadow = requests.post(shadow_url, json=shadow_params)

file_name = 'shadow.geotiff' # change the file name and storage location here
# save as geotiff file
with open(file_name, "wb") as f:
        f.write(shadow.content)
        f.close()


# #
import rasterio
from rasterio.plot import show

img = rasterio.open(file_name)
show(img)