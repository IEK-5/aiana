from apv.classes.apv_rad_texts.morschenich import Morschenich
from apv.classes.apv_rad_texts.geometry_basics import GeomBasics
from apv.classes.util_classes.settings_handler import Settings


class GeometriesHandler(GeomBasics):
    """
    to create the radiance text string for the oct file builder
    methods are forwarded so that they are called only uppon using
    """

    def __init__(self, settings: Settings):
        super().__init__(settings)

    def morschenich_fixed(self):
        return Morschenich(self.settings).morschenich_fixed()
