import numpy as np
import pandas as pd
import itertools


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


def create_parameters_permutated_df(parameters, exclude=[]) -> pd.DataFrame:
    # create list from parameters object:
    parameters_list = []
    for attribute in dir(parameters):
        if not attribute.startswith('__') and not callable(
                getattr(parameters, attribute)):

            if attribute not in exclude:
                parameters_list += [attribute]

    # get ranges
    parameter_ranges = []
    for attribute in parameters_list:
        parameter_ranges += [getattr(parameters, attribute)]

    data = list(itertools.product(*parameter_ranges))
    sim_IDs = range(1, len(data)+1)
    # fill in config attributes into the dataframe
    df = pd.DataFrame(data, index=sim_IDs, columns=parameters_list)
    df.index.names = ['sim_ID']
    return df
