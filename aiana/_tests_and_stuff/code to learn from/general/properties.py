# #
class C:
    def __init__(self):
        self.b = 2

    @property
    def x(self):
        return self.b * 2


# #
c = C()
c.x
# #
c.b = 3
c.x

# #
class C:
    def __init__(self):
        self.b = 2

    def set_x(self):
        self.x = self.b * 2

# #
c = C()
c.x
# #
c.b = 3
c.set_x()
c.x
# #
