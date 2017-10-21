from deepcoder.dsl.types import INT, LIST

class Value(object):
    def __init__(self, val, typ):
        self._val = val
        self._typ = typ

    @property
    def type(self):
        return self._typ

    @property
    def val(self):
        return self._val

    def __hash__(self):
        if self.type == LIST:
            return hash(tuple(self.val))
        return self.val

    def __eq__(self, other):
        if not isinstance(other, Value):
            return False
        return self.val == other.val and self.type == other.type

    def __repr__(self):
        return str(self.val)

    @classmethod
    def construct(self, val, typ=None):
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

