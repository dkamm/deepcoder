class Variable(object):
    def __init__(self, name, x, t):
        self._name = name
        self._x = x
        self._type = t

    @property
    def name(self):
        return self._name

    @property
    def x(self):
        return self._x

    @property
    def type(self):
        return self._type

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        if not isinstance(other, Variable):
            return False
        return self.name == other.name and self.x == other.x and self.type == other.type

    def __repr__(self):
        return str(self.name)
