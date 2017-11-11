class PrimitiveType(object):
    def __init__(self, name):
        self.name = name
        self._hash = hash(self.name)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

INT = PrimitiveType('INT')
BOOL = PrimitiveType('BOOL')
LIST = PrimitiveType('LIST')
NULLTYPE = PrimitiveType('NULL')

class FunctionType(PrimitiveType):
    def __init__(self, input_type, output_type):
        name = 'F(' + str(input_type) + ', ' + str(output_type) + ')'
        super(FunctionType, self).__init__(name)
        self.input_type = input_type
        self.output_type = output_type
        # iterable
        self.input_types = (input_type,) if not isinstance(input_type, tuple) else input_type