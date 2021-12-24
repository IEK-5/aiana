
import pandas as pd
import itertools


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


def get_attribute_names(class_or_object, exclude=[]):
    """geht so viel einfacher:
    class MyClass:
    def __init__(self,name,score):
        self.name = name
        self.score = score
        self.grade = None

    MyObj = MyClass('leo', 1337)
    list(MyObj.__dict__)



    """
    # create list from parameters object:
    attribute_list = []
    for attribute in dir(class_or_object):
        if not attribute.startswith('__') and not callable(
                getattr(class_or_object, attribute)):

            if attribute not in exclude:
                attribute_list += [attribute]
    return attribute_list
