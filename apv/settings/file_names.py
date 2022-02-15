from apv.settings.simulation import Simulation
from apv.settings.apv_systems import Default as APV_System


class Names:
    study: str # also used as first part of the
    # Radiance scene file name (.oct) and the output files
    csv_fn: str  # fn = file name
    jpg_fn: str
    oct_fn: str

    def __init__(self, SimSettings: Simulation,
                 APV_SystSettings: APV_System):

        self.study: str = 'APV_Floating'

        self.csv_fn = SimSettings.sim_date_time.replace(':', 'h')+'.csv'

        self.jpg_fn = self.csv_fn.replace('.csv', '.jpg')

        self.oct_fn = self.study + '_' \
            + APV_SystSettings.module_form + '_' \
            + self.csv_fn.replace('.csv', '.oct')
