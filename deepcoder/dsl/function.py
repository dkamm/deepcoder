from deepcoder.dsl import constants
from deepcoder.dsl.value import Value, IntValue, ListValue, NULLVALUE
from deepcoder.dsl.types import FunctionType

class OutputOutOfRangeError(Exception):
    pass

class NullInputError(Exception):
    pass

def in_range(val):
    if isinstance(val, IntValue):
        val = ListValue([val.val])
    for x in val.val:
        if x < constants.INTMIN or x > constants.INTMAX:
            return False
    return True

class Function(Value):
    def __init__(self, name, f, input_type, output_type):
        super(Function, self).__init__(f, FunctionType(input_type, output_type))
        self.name = name

    def __call__(self, *args):
        for arg in args:
            if arg == NULLVALUE:
                raise NullInputError('{}({})'.format(self.name, args))
        raw_args = [x.val for x in args]
        output_raw = self.val(*raw_args)
        output_val = Value.construct(output_raw, self.output_type)
        if output_val != NULLVALUE and not in_range(output_val):
            raise OutputOutOfRangeError('{}({})'.format(self.name, args))
        return output_val

    @property
    def input_type(self):
        return self.type.input_type

    @property
    def output_type(self):
        return self.type.output_type

    def __eq__(self, other):
        if not isinstance(other, Function):
            return False
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name #+ '(' + str(self.input_type) + ',' + str(self.output_type + ')'