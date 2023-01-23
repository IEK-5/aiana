""" This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>."""

from typing import Literal
from pathlib import Path
import pandas as pd


class ViewSettings:
    def __init__(self):
        # Accelerad settings ####################
        # need to be installed first https://nljones.github.io/Accelerad/index.html
        self.use_acceleradRT_view = True  # real time scene navigation and viewing

        self.accelerad_img_height: int = 780  # [pixel]
        # NOTE img_width is calculated from the view angles to avoid distortion

        self.scene_camera_dicts: dict = {  
            'total': {'cam_pos_x': 19.8,   # depth
                      'cam_pos_y': -22.4,   # left / right
                      'cam_pos_z': 18.8,     # height
                      'view_direction_x': -0.581,
                      'view_direction_y': 0.6118,
                      'view_direction_z': -0.5361,
                      'horizontal_view_angle': 80,  # [degree]
                      'vertical_view_angle': 45,  # [degree]
                      },
            'top_down': {'cam_pos_x': 0,   # depth
                         'cam_pos_y': 0,   # left / right
                         'cam_pos_z': 10,     # height
                         'view_direction_x': 0,
                         'view_direction_y': 0.001,
                         'view_direction_z': -1,
                         'horizontal_view_angle': 64,  # [degree]
                         'vertical_view_angle': 36,  # [degree]
                         },
            'close_up': {'cam_pos_x': 11.7356,   # depth
                         'cam_pos_y': 6.55262,   # left / right
                         'cam_pos_z': 11.0956,     # height
                         'view_direction_x': -0.6964,
                         'view_direction_y': 0.4769,
                         'view_direction_z': -0.5363,
                         'horizontal_view_angle': 76.5895,  # [degree]
                         'vertical_view_angle': 42.5897,  # [degree]
                         },
            'as_heatmap': {'cam_pos_x': 11.7356,   # depth
                           'cam_pos_y': 6.55262,   # left / right
                           'cam_pos_z': 11.0956,     # height
                           'view_direction_x': -0.6964,
                           'view_direction_y': 0.4769,
                           'view_direction_z': -0.5363,
                           'horizontal_view_angle': 46,  # [degree]
                           'vertical_view_angle': 40,  # [degree]
                           },
        }

        """
        # morschenich:
        scene_camera_dicts = Default.scene_camera_dicts.copy()
        scene_camera_dicts['total'] = {'cam_pos_x': -29,   # depth
                                    'cam_pos_y': 5,   # left / right
                                    'cam_pos_z': 5.5,     # height
                                    'view_direction_x': 0.9863,
                                    'view_direction_y': -0.1567,
                                    'view_direction_z': -0.0509,
                                    'horizontal_view_angle': 100,  # [degree]
                                    'vertical_view_angle': 75  # [degree]
                                    }
        """
