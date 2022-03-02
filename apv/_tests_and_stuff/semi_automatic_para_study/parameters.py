import numpy as np


class Parameters():
    def __init__(self, resolution: str):

        if resolution == 'fine':
            self.tilt = np.arange(0, 56, 2)
            # self.azimut = np.arange(150, 211, 1)
            self.gcr = np.arange(0.1, 1.01, 0.05)  # ground covering ratio

        if resolution == 'coarse':
            self.tilt = np.arange(15, 56, 15)
            # self.azimut = np.arange(150, 211, 15)
            self.gcr = np.arange(0.5, 1.001, 0.25)  # ground covering ratio
