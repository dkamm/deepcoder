
import copy

import numpy as np

from deepcoder.dsl import impl
from deepcoder.dsl.function import OutputOutOfRangeError, NullInputError
from deepcoder.dsl.constants import INTMIN, INTMAX
from deepcoder.dsl.types import INT, LIST
from deepcoder.dsl.value import Value

L = 20 # max length of list

class InvalidConstraintError(Exception):
    pass

class IntConstraint(object):
    """Int range constraint.

    Attributes:
        vmin (int): minimum value
        vmax (int): maximum value
    """
    def __init__(self, vmin=INTMIN, vmax=INTMAX):
        self.vmin = vmin
        self.vmax = vmax

    @property
    def valid(self):
        return self.vmax >= self.vmin

    def __eq__(self, other):
        return self.vmin == other.vmin and self.vmax == other.vmax

    def __repr__(self):
        return '[{},{}]'.format(self.vmin, self.vmax)

    def apply(self, other):
        self.vmax = min(self.vmax, other.vmax)
        self.vmin = max(self.vmin, other.vmin)

class ListConstraint(object):
    """Constraints on a list.

    Attributes:
        lmin (int): min length
        lmax (int): max length
        int_constaints (list): list of IntConstraint representing constraints
            on int range for each list length. Relevant for SCAN1L.
    """
    def __init__(self, lmin=1, lmax=L, int_constraints=None):
        self.lmin = lmin
        self.lmax = lmax
        if int_constraints:
            self._int_constraints = int_constraints
        else:
            self._int_constraints = [IntConstraint() for _ in range(L + 1)]

        self._adjust()

    @property
    def int_constraints(self):
        return self._int_constraints[:self.lmax+1]


    @property
    def valid(self):
        if self.lmax < self.lmin:
            return False
        return sum([x.valid for x in self.int_constraints[self.lmin:self.lmax+1]]) == (self.lmax - self.lmin + 1)

    def __eq__(self, other):
        return (self.lmin == other.lmin and
                self.lmax == other.lmax and
                not sum([x != y for x, y in zip(self.int_constraints, other.int_constraints)]))

    def __repr__(self):
        return '({},{}){}'.format(self.lmin, self.lmax, self.int_constraints)


    def _adjust(self):
        """Adjusts lmin/lmax based on the validity of the int_constraints."""
        lmax = 0
        lmin = len(self.int_constraints)
        for  i, ic in enumerate(self.int_constraints):
            if ic.valid:
                lmax = max(lmax, i)
                lmin = min(lmin, i)

        self.lmax = min(lmax, self.lmax)
        self.lmin = max(lmin, self.lmin)

    def apply(self, other):
        self.lmax = min(self.lmax, other.lmax)
        self.lmin = max(self.lmin, other.lmin)
        for my_ic, other_ic in zip(self.int_constraints, other.int_constraints):
            my_ic.apply(other_ic)
        self._adjust()

def sample(constraint):
    if not constraint.valid:
        raise InvalidConstraintError('invalid constraint {}'.format(constraint))

    if isinstance(constraint, IntConstraint):
        if constraint.vmin == constraint.vmax:
            return constraint.vmin
        return np.random.randint(constraint.vmin, constraint.vmax)
    elif isinstance(constraint, ListConstraint):
        if constraint.lmin == constraint.lmax:
            l = constraint.lmin
        elif constraint.lmin < constraint.lmax:
            l = np.random.randint(constraint.lmin, constraint.lmax)
        ic = constraint.int_constraints[l]
        return [sample(ic) for _ in range(l)]

def get_constraints_from_stmt(stmt, constraint, null_allowed=False):
    """Returns a list of constraint to apply to inputs of stmt or None which means
    no constraint imposed.

    Example:
        MAP,*2,0

        The output of this is a ListConstraint.  Each element of list constraint is
        the int constraint for a list of length L.  We have a constraint for each list length
        since some are length dependent like SCAN1L

    The following functions impose constraints on the ranges of their inputs:

    TAKE, DROP, ACCESS- index must be positive.

    MAP- depends on the lambda (*2 shrinks the range, //2 does not)

    ZIPWITH- depends on the lambda. for +, we can constrain int range to [-256/2, 256/2].
        for *, it is [-sqrt(256), sqrt(256)]

    SCAN1L- depends on the lambda. for example, if L = 5,
        then for + the constraint could be [-256/5, 256/5] (sum of all elements is gauranteed
        not to exceed bounds). but if L = 10, we would want [-256/10, 256/10].

    Arguments:
        stmt (tuple): statement to consider.
        constraint (IntConstraint or ListConstraint): constraint on output
            of stmt.
        null_allowed(bool): True if statement allowed to output null, False otherwise. 
            Relevant for HEAD, TAIL, ACCESS which can output NULL.
    """
    f, inputs = stmt

    if f == impl.MAP:
        lmbda = inputs[0]
        int_constraints = []
        for ic in constraint.int_constraints:
            vmax = ic.vmin
            vmin = ic.vmax

            if lmbda == impl.PLUS1:
                vmax = ic.vmax - 1
                vmin = ic.vmin - 1

            elif lmbda == impl.MINUS1:
                vmax = ic.vmax + 1
                vmin = ic.vmin + 1

            elif lmbda == impl.TIMES2:
                vmax = int(ic.vmax / 2)
                vmin = int(ic.vmin / 2)

            elif lmbda == impl.TIMES3:
                vmax = int(ic.vmax / 3)
                vmin = int(ic.vmin / 3)

            elif lmbda == impl.TIMES4:
                vmax = int(ic.vmax / 4)
                vmin = int(ic.vmin / 4)

            elif lmbda == impl.DIV2:
                vmax = int(ic.vmax * 2)
                vmin = int(ic.vmin * 2)

            elif lmbda == impl.DIV3:
                vmax = int(ic.vmax * 3)
                vmin = int(ic.vmin * 3)

            elif lmbda == impl.DIV4:
                vmax = int(ic.vmax * 4)
                vmin = int(ic.vmin * 4)

            elif lmbda == impl.TIMESNEG1:
                vmax = -ic.vmin
                vmin = -ic.vmax

            elif lmbda == impl.POW2:
                min_abs = min(abs(ic.vmax), abs(ic.vmin))
                vmax = int(np.sign(ic.vmax) * np.sqrt(min_abs))
                vmin = int(np.sign(ic.vmin) * np.sqrt(min_abs)) # take sqrt vmax since square of negative is positive

            # clip
            vmax = min(vmax, INTMAX)
            vmin = max(vmin, INTMIN)

            int_constraints.append(IntConstraint(vmin, vmax))

        return [ListConstraint(constraint.lmin, constraint.lmax, int_constraints)]

    elif f == impl.ACCESS:
        if null_allowed:
            return [IntConstraint(vmin=0),
                    ListConstraint(int_constraints=[copy.copy(constraint) for _ in range(L + 1)])]
        else:
            # have to clip to 0 since list length may be 1
            return [IntConstraint(vmin=0, vmax=0),
                    ListConstraint(lmin=1, int_constraints=[copy.copy(constraint) for _ in range(L + 1)])]

    elif f in [impl.TAKE, impl.DROP]:
        return [IntConstraint(vmin=0),
                constraint]

    elif f == impl.ZIPWITH:
        lmbda, _, _ = inputs

        int_constraints = []
        for ic in constraint.int_constraints:
            vmin = ic.vmin
            vmax = ic.vmax

            if lmbda in [impl.LPLUS, impl.LMINUS]:
                vmax = int(ic.vmax / 2)
                vmin = int(ic.vmin / 2)
            elif lmbda == impl.LTIMES:
                min_abs = min(abs(ic.vmax), abs(ic.vmin))
                vmax = int(np.sign(ic.vmax) * np.sqrt(min_abs).astype(int))
                vmin = int(np.sign(ic.vmin) * np.sqrt(min_abs).astype(int))

            # clip
            vmax = min(vmax, INTMAX)
            vmin = max(vmin, INTMIN)

            int_constraints.append(IntConstraint(vmin, vmax))

        return [ListConstraint(constraint.lmin, constraint.lmax, int_constraints)] * 2

    elif f == impl.SCAN1L:
        lmbda, _ = inputs
        int_constraints = []
        for l, ic in enumerate(constraint.int_constraints):
            if l == 0:
                int_constraints.append(ic)
                continue

            vmin = ic.vmin
            vmax = ic.vmax

            if lmbda in [impl.LPLUS, impl.LMINUS]:
                vmax = int(ic.vmax / l)
                vmin = int(ic.vmin / l)
            elif lmbda == impl.LTIMES:
                min_abs = min(abs(ic.vmax), abs(ic.vmin))
                vmax = int(np.sign(ic.vmax) * 10 ** (np.log10(min_abs) / l))
                vmin = int(np.sign(ic.vmin) * 10 ** (np.log10(min_abs) / l))

            # clip
            vmax = min(vmax, INTMAX)
            vmin = max(vmin, INTMIN)

            int_constraints.append(IntConstraint(vmin, vmax))
        return [ListConstraint(constraint.lmin, constraint.lmax, int_constraints)]
    elif f == impl.SUM:
        int_constraints = []
        for l in range(L):
            if l == 0:
                int_constraints.append(constraint)
                continue

            int_constraints.append(IntConstraint(int(constraint.vmin / l),
                int(constraint.vmax / l)))
        return [ListConstraint(int_constraints=int_constraints)]

    elif f in [impl.COUNT]:
        # no constraint
        return [ListConstraint()]

    elif f in [impl.HEAD, impl.TAIL]:
        if null_allowed:
            # list constrained to int constraint
            return [ListConstraint(int_constraints=[constraint] * L)]
        else:
            int_constraints = []
            for l in range(L+1):
                int_constraints.append((IntConstraint(0, l-1)))
            return [ListConstraint(int_constraints=int_constraints)]

    elif f in [impl.MINIMUM, impl.MAXIMUM]:
        # list constrained to int constraint
        return [ListConstraint(int_constraints=[constraint] * L)]

    elif f in [impl.FILTER, impl.REVERSE, impl.SORT]:
        # these pipe just through constraint of output
        return [constraint]

    raise ValueError('bad stmt {}'.format(stmt))

def propagate_constraints(p, output_constraint=None):
    """Returns the constraints on inputs for a program."""
    constraints = []

    for typ in p.types:
        if typ == INT:
            constraint = IntConstraint()
        elif typ == LIST:
            constraint = ListConstraint()
        constraints.append(constraint)

    if output_constraint:
        # constrain last statement
        constraints[-1] = output_constraint

    def _get_input_indices(stmt):
        _, inputs = stmt
        return [x for x in inputs if isinstance(x, int)]

    null_allowed = [True] * len(p.types)
    for i, stmt in enumerate(reversed(p.stmts)):
        idx = len(p.types) - 1 - i
        original_constraint = constraints[idx]
        implied_constraints = get_constraints_from_stmt(stmt, original_constraint, null_allowed[idx])
        if implied_constraints:
            input_indices = _get_input_indices(stmt)
            input_constraints = [constraints[x] for x in input_indices]
            for implied_constraint, input_constraint in zip(implied_constraints, input_constraints):
                input_constraint.apply(implied_constraint)
            for input_idx in input_indices:
                null_allowed[input_idx] = False
    return constraints

def get_input_output_examples(program, M=5):
    examples = []
    constraints = propagate_constraints(program)

    for i in range(M):
        input_vals = []
        for j, (input_type, constraint) in enumerate(zip(program.input_types, constraints)):
            raw_val = sample(constraint)
            val = Value.construct(raw_val, input_type)
            input_vals.append(val)
        output_val = program(*input_vals)
        examples.append((input_vals, output_val))

    return examples

def is_same(program, other, input_output_examples=None, M=5):
    """input_output_examples can be passed in for speed
    (comparing same program to many others)"""
    try:
        if (program.input_types != other.input_types or
            program.types[-1] != other.types[-1]):
            return False
        if not input_output_examples:
            input_output_examples = get_input_output_examples(program, M)
        for inputs, output in input_output_examples:
            other_output = other(*inputs)
            if output != other_output:
                return False
        return True
    except (OutputOutOfRangeError, NullInputError):
        return False