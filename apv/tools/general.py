
def get_attribute_names(class_or_object, exclude=[]):
    # create list from parameters object:
    attribute_list = []
    for attribute in dir(class_or_object):
        if not attribute.startswith('__') and not callable(
                getattr(class_or_object, attribute)):

            if attribute not in exclude:
                attribute_list += [attribute]
    return attribute_list
