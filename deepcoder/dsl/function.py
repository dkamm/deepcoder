class FunctionType(object):
    def __init__(self, input_type, output_type):
        self.input_type = input_type
        self.output_types = output_type

    def __eq__(self, other):
        if isinstance(other, FunctionType):
            return (self.input_type == other.input_type and
                    self.output_type == other.output_type)

class Function(object):
    def __init__(self, f, input_type, output_type):
        self.f = f
        self.input_type = input_type
        self.output_type = output_type

    @property
    def type(self):
        return FunctionType(self.input_type, self.output_type)

