
INT = 0
BOOL = 1
LIST = 2

class Variable(object):
    def __init__(self, x, t):
        self.x = x
        self._type = t

    @property
    def type(self):
        return self._type
