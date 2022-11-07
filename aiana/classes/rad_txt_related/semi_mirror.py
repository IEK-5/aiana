import numpy as np
from aiana.classes.rad_txt_related.geometry_basics import GeomBasics
from aiana.classes.util_classes.settings_handler import Settings


class SemiMirror(GeomBasics):
    """uses coordinates such as apv system south west corner and
    methods such as inclined_tables from the GeomBasics class by
    inherence"""

    def __init__(self, settings: Settings):
        super().__init__(settings)

    def semi_mirror(self) -> str: