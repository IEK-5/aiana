# #
from apv.anti_bug_testing.tester_class import Tester

if __name__ == '__main__':
    testerObj = Tester(open_oct_viewer=True)
    testerObj.test_inverted_bool_settings(['use_acceleradRT_view'])
