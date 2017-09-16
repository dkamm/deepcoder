class PrimitiveType(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

INT = PrimitiveType('INT')
BOOL = PrimitiveType('BOOL')
LIST = PrimitiveType('LIST')

class FunctionType(object):
    def __init__(self, input_type, output_type):
        self.input_type = input_type
        self.output_type = output_type
        # iterable
        self.input_types = (input_type,) if not isinstance(input_type, tuple) else input_type


    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, FunctionType):
            return (self.input_type == other.input_type and
                    self.output_type == other.output_type)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'F(' + str(self.input_type) + ', ' + str(self.output_type) + ')'

