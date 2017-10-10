from deepcoder.dsl.types import FunctionType

class Function(object):
    def __init__(self, name, f, input_type, output_type):
        self.name = name
        self.f = f
        self.input_type = input_type
        self.output_type = output_type

    def __call__(self, *args):
        return self.f(*args)

    @property
    def x(self):
        return self.f

    @property
    def type(self):
        return FunctionType(self.input_type, self.output_type)

    #def __eq__(self, other):
    #    return self.name == other.name

    #def __hash__(self):
    #    return hash(self.name)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name #+ '(' + str(self.input_type) + ',' + str(self.output_type + ')'

