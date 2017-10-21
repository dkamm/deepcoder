from deepcoder.dsl.value import Value
from deepcoder.dsl.types import FunctionType

class Function(Value):
    def __init__(self, name, f, input_type, output_type):
        super(Function, self).__init__(f, FunctionType(input_type, output_type))
        self.name = name

    def __call__(self, *args):
        raw_args = [x.val for x in args]
        output_val = self.val(*raw_args)
        return Value.construct(output_val, self.output_type)

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

