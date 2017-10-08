
import numpy as np

MININT = -256
MAXINT = 256

L = 20 # max length of list

class IntConstraint(object):
    def __init__(self, vmin=MININT, vmax=MAXINT):
        self.vmin = vmin
        self.vmax = vmax

    def valid(self):
        return self.vmax >= self.vmin


class ListConstaint(object):
    """
    Attributes:
        lmin (int): min length
        lmax (int): max length
        int_constaints (list): constraints on each
            index.
    """
    def __init__(self, lmin=1, lmax=L, int_constraints=None):
        self.lmin = lmin
        self.lmax = lmax
        if int_constraints:
            self.int_constraints = int_constraints
        else:
            self.int_constraints = [IntConstraint()] * L

    def valid(self):
        if self.lmax < self.lmin:
            return False
        return sum([x.valid for x in self.int_constraints[:self.lmax]]) == self.lmax


def sample(constraint):
    if isinstance(constraint, IntConstraint):
        return np.random.randint(constraint.vmin, constraint.vmax)
    elif isinstance(constraint, ListConstraint):
        l = np.random.randint(constraint.lmin, constraint.lmax)
        return [np.random.randint(x.vmin, x.vmax) for x in constraint.int_constraints[:l]]


def _propagate_constraint(stmt, constraint, constraints):
    f, inputs = stmt

    if f == impl.MAP:
        lmbda = inputs[0]
        idx = inputs[1]
        next_constraint = constraints[idx]

        for curint, nextint in zip(constraint.int_constraints,
                                   next_constraint.int_constraints):
            if lmbda == impl.PLUS1:
                nextint.vmax = curint.vmax - 1
                nextint.vmin = curint.vmin - 1

            elif lmbda == impl.MINUS1:
                nextint.vmax = curint.vmax + 1
                nextint.vmin = curint.vmax + 1

            elif lmbda == impl.TIMES2:
                nextint.vmax = curint.vmax // 2
                nextint.vmin = curint.vmin // 2

            elif lmbda == impl.TIMES3:
                nextint.vmax = curint.vmax // 3
                nextint.vmin = curint.vmin // 3


            elif lmbda == impl.TIMES4:
                nextint.vmax = curint.vmax // 4
                nextint.vmin = curint.vmin // 4

            elif lmbda == impl.TIMESNEG1:
                nextint.vmax = -curint.vmin
                nextint.vmin = -curint.vmax

            elif lmbda == impl.POW2:
                nextint.vmax = np.sign(curint.vmax) * np.sqrt(abs(curint.vmax))
                nextint.vmin = np.sign(curint.vmin) * np.sqrt(abs(curint.vmin))

            # clip
            nextint.vmax = min(nextint.vmax, INTMAX)
            nextint.vmin = max(nextint.vmin, INTMIN)

    elif f in [impl.TAKE, impl.DROP, impl.ACCESS]:
        idx = inputs[0]
        next_constraint = constraints[idx]
        next_constraint.vmin = max(next_constraint.vmin, 0)
        next_constraint.vmax = min(next_constraint.vmax, 0)

    elif f == impl.ZIPWITH:

    elif f == impl.SCAN1L:
        # TODO: how would this be implemented?
        # For instance, if lambda is *, then would max need to be 10^{log 256 / L},
        # where L is the max length of the list?
        # This seems overly restrictive.
        pass

def get_constraints(p):
    constraints = []

    for typ in p.types:
        if typ == INT:
            constraint = IntConstraint()
        elif typ == LIST:
            constraint = ListConstraint()
        constraints.append(constraint)

    for i, stmt in reversed(p.stmts):
        idx = i + len(p.input_types)
        constraint = constraints[idx]
        _propagate_constraint(stmt, constraint, constraints)


    return constraints

def get_input_output_examples(p, M=5):
    constraints = get_constraints(p)

    examples = []

    for i in range(M):
        inputs = []
        for constraint in constraints[:len(p.input_types)]:
            inputs.append(sample(constraint))
        output = p(*inputs)
        examples.append((inputs, output))

    return examples
