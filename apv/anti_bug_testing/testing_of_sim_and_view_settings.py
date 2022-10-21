# #
from apv.anti_bug_testing.tester_class import Tester


def run_sim_settings_test(**kwargs):
    """**kwargs:
        mode (optional): Defaults to 'test'
        (which means 1. simulate 2. check and plot difference to reference)
            alternative: 'create_reference'

        open_oct_viewer (bool, optional): to check scene creation for each set.
        Viewer needs to be closed manualy. Defaults to False.

        default_settings (Settings, optional): Defaults to None (constructing
            automatically based on setting files)

        run_simulation (bool, optional): Defaults to True, can be set False,
            if only viewing is of interest.
    """
    testerObj = Tester(**kwargs)
    testerObj.test_listItems_separately("rtraceAccuracy", [
        'std', 'accurate', 'hq', 'good_no_interp', 'acc_no_interp'])


# #
# view settings
if __name__ == '__main__':
    testerObj = Tester(open_oct_viewer=True)
    testerObj.test_inverted_bool_settings(['use_acceleradRT_view'])
