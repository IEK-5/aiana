from apv.settings.simulation import Simulation
from apv.settings.apv_systems import Default as SystSettings
from apv.settings.file_names import Names
from apv.settings.user_paths import UserPaths


class Settings:
    def __init__(
        self,
        SimSettings: Simulation = None,
        APV_SystSettings: SystSettings = None,
        paths: UserPaths = None,
        names: Names = None
    ):

        if SimSettings is None:
            self.sim = Simulation()
        else:
            self.sim = SimSettings

        if APV_SystSettings is None:
            self.apv = SystSettings()
        else:
            self.apv = APV_SystSettings

        if names is None:
            self.names = Names(self.sim, self.apv)
        else:
            self.names = names

        if paths is None:
            self.paths = UserPaths(self.names)
        else:
            self.paths = paths
