from deepcoder.dsl import constants
from deepcoder.dsl.types import INT, LIST, NULLTYPE

class Value(object):
    def __init__(self, val, typ):
        self._val = val
        self._typ = typ
        self._name = str(self._val)
        if self._typ == LIST:
            self._hash = hash(tuple(val))
        else:
            self._hash = hash(val)

    @property
    def type(self):
        return self._typ

    @property
    def val(self):
        return self._val

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, Value):
            return False
        return self.val == other.val and self.type == other.type

    def __str__(self):
        return self._name

    def __repr__(self):
        return self._name

    @classmethod
    def construct(self, val, typ=None):
        if val is None:
            return NULLVALUE

        if typ is None:
            raw_type = type(val)
            if raw_type == int:
                typ = INT
            elif raw_type == list:
                typ = LIST

        if typ == INT:
            return IntValue(val)
        elif typ == LIST:
            return ListValue(val)
        raise ValueError('bad type {}'.format(typ))

class IntValue(Value):
    def __init__(self, val):
        super(IntValue, self).__init__(val, INT)

class ListValue(Value):
    def __init__(self, val):
        super(ListValue, self).__init__(val, LIST)

NULLVALUE = Value(None, NULLTYPE)