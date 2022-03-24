from typing import Literal
from pathlib import Path
import pandas as pd


class ViewSettings:

    accelerad_img_width: int = 1400  # [pixel]
    # NOTE img_height is calculated from the view angles to avoid distortion

    scene_camera_dicts: dict = {  # TODO besser auch norden hinten machen
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
