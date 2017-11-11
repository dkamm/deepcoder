
import numpy as np

from deepcoder.dsl.constants import INTMIN, INTMAX
from deepcoder.dsl.types import INT, LIST
from deepcoder.dsl.impl import NAME2FUNC
from deepcoder.dsl.function import Function
from deepcoder.dsl.value import IntValue, ListValue, NULLVALUE

# Parsed program

# statement: (function, (input0, input1, ..., inputn))

def get_unused_indices(program):
    """Returns unused indices of variables/statements in program."""
    used = set()
    for (_, inputs) in program.stmts:
        used |= set(inputs)
    all_indices = set(range(len(program.types) -1))
    return all_indices - used

def prune(program):
    N = len(program.input_types) + len(program.stmts)

    offsets = [0] * N
    unused_indices = sorted(list(get_unused_indices(program)))
    for i in unused_indices:
        for j in range(i, N):
            offsets[j] -= 1

    input_types = []
    for i, input_type in enumerate(program.input_types):
        if i not in unused_indices:
            input_types.append(input_type)

    stmts = []
    for i, (f, args) in enumerate(program.stmts):
        idx = i + len(program.input_types)
        if idx not in unused_indices:
            new_args = []
            for arg in args:
                if isinstance(arg, int):
                    arg += offsets[arg]
                new_args.append(arg)
            stmts.append((f, new_args))

    return Program(input_types, stmts)

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
        self._hash = hash(self.prefix)

    def functions(self):
        for func, args in self.stmts:
            yield func
            for arg in args:
                if isinstance(arg, Function):
                    yield arg

    def toprefix(self):
        toks = [x.name for x in self.input_types]
        for f, inputs in self.stmts:
            tok = ','.join(map(str, [f] + list(inputs)))
            toks.append(tok)

        return '|'.join(toks)

    def __str__(self):
        return self.prefix

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

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
            return NULLVALUE
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