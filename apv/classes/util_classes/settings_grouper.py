from apv.settings.simulation import Simulation
from apv.settings.apv_systems import Default as SystSettings
from apv.settings.file_names import Names
from apv.settings.user_paths import UserPaths


class Settings:
    def __init__(self):
        self.sim = Simulation()
        self.apv = SystSettings()
        self.set_names_and_paths()

    def set_names_and_paths(self):
        self.names = Names(self.sim, self.apv)
        self.paths = UserPaths(self.names)
