
import numpy as np

from deepcoder.dsl.constants import NULL
from deepcoder.dsl.types import INT, LIST
from deepcoder.dsl.impl import NAME2FUNC

# Parsed program

# statement: (function, (input0, input1, ..., inputn))

def prune(program):
    N = len(program.input_types) + len(program.stmts)

    offsets = [0] * N
    useds = [True] * N

    def get_is_used(i):
        for _, inputs in program.stmts:
            for x in inputs:
                if x == i:
                    return True

    for i in range(N):
        used = get_is_used(i) or i == N - 1
        if not used:
            for j in range(i+1, N):
                offsets[j] -= 1
        useds[i] = used

    input_types = []
    for i, input_type in enumerate(program.input_types):
        if useds[i]:
            input_types.append(input_type)

    stmts = []
    for i, (f, inputs) in enumerate(program.stmts):
        if not useds[i + len(program.input_types)]:
            continue
        new_inputs = []
        for x in inputs:
            if isinstance(x, int):
                x += offsets[x]
            new_inputs.append(x)
        stmts.append((f, new_inputs))

    return Program(input_types, stmts)

def gen_inputs(input_types, maxlen=20, intrange=256):
    inputs = []
    for input_type in input_types:
        if input_type == INT:
            # We restrict INTs to [0,maxlen)
            # because INT can only be used for array access
            # via TAKE, DROP, ACCESS in the DSL
            x = np.random.randint(0, maxlen)
        else:
            l = np.random.randint(0, maxlen)
            x = list(np.random.randint(-intrange, intrange, l))

        inputs.append(x)

    return inputs

def is_same(lhs, rhs, N=5, maxlen=20):
    if lhs.input_types != rhs.input_types:
        return False

    inputs_list = [gen_inputs(lhs.input_types, maxlen) for _ in range(N)]

    lhs_outputs = [lhs(*inputs) for inputs in inputs_list]
    rhs_outputs = [rhs(*inputs) for inputs in inputs_list]

    for lhs_output, rhs_output in zip(lhs_outputs, rhs_outputs):
        if lhs_output != rhs_output:
            return False

    return True

class Program(object):
    """
    Attributes:
        input_types (tuple): tuple of Type (INT,LIST) representing inputs
        stmts (tuple): tuple of statements. each statement is pair of function, tuple of mixed type representing arguments
        types (tuple): tuple of Type for all variables
        prefix (str): prefix string that completely describes program
    """
    def __init__(self, input_types, stmts):
        self.input_types = tuple(input_types)
        self.stmts = tuple(stmts)
        self.types = tuple(list(self.input_types) + [f.type.output_type for f, _ in self.stmts])
        self.prefix = self.toprefix()

    def toprefix(self):
        toks = [x.name for x in self.input_types]
        for f, inputs in self.stmts:
            tok = ','.join(map(str, [f] + list(inputs)))
            toks.append(tok)

        return '|'.join(toks)

    def __str__(self):
        return self.toprefix()

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(self.toprefix())

    def __eq__(self, other):
        return self.prefix == other.prefix

    def __lt__(self, other):
        #if len(self.types) < len(other.types):
        #    return True
        return self.prefix < other.prefix

    @classmethod
    def parse(cls, prefix):
        input_types = []
        stmts = []

        def get_stmt(term):
            stmt = []
            for inner in term.split(','):
                if inner.isdigit():
                    stmt.append(int(inner))
                else:
                    stmt.append(NAME2FUNC[inner])
            return stmt[0], tuple(stmt[1:])

        for tok in prefix.split('|'):
            if ',' in tok:
                stmts.append(get_stmt(tok))
            else:
                if tok == INT.name:
                    typ = INT
                elif tok == LIST.name:
                    typ = LIST
                else:
                    raise ValueError('invalid input type {}'.format(tok))
                input_types.append(typ)

        return Program(input_types, tuple(stmts))

    def __call__(self, *inputs):
        if not self.stmts:
            return NULL
        vals = list(inputs)
        for f, inputs in self.stmts:
            args = []
            for input in inputs:
                if isinstance(input, int):
                    args.append(vals[input])
                else:
                    args.append(input)
            val = f(*args)
            vals.append(val)
        return vals[-1]

