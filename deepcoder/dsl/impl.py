import collections

from deepcoder.dsl.variable import INT, BOOL, LIST
from deepcoder.dsl.function import Function, FunctionType

# first order functions
HEAD = Function(lambda xs: xs[0] if xs else None, LIST, INT)
TAIL = Function(lambda xs: xs[-1] if xs else None, LIST, INT)
TAKE = Function(lambda n, xs: xs[:n], (INT, LIST), LIST)
DROP = Function(lambda n, xs: xs[n:], (INT, LIST), LIST)
ACCESS = Function(lambda n, xs: xs[n] if n >= 0 and len(xs) > n else None, (INT, LIST), LIST)
MINIMUM = Function(min, LIST, INT)
MAXIMUM = Function(max, LIST, INT)
REVERSE = Function(lambda xs: xs[::-1], LIST, LIST)
SORT = Function(sorted, LIST, LIST)
SUM = Function(sum, LIST, INT)

FIRSTORDER = [HEAD, TAIL, TAKE, DROP, ACCESS, MINIMUM, MAXIMUM, REVERSE, SORT, SUM]

# lambdas
PLUS1 = Function(lambda x: x + 1, INT, INT)
MINUS1 = Function(lambda x: x - 1, INT, INT)
TIMES2 = Function(lambda x: x * 2, INT, INT)
DIV2 = Function(lambda x: x // 2, INT, INT)
TIMESNEG1 = Function(lambda x: -x, INT, INT)
POW2 = Function(lambda x: x ** 2, INT, INT)
TIMES3 = Function(lambda x: x * 3, INT, INT)
DIV3 = Function(lambda x: x // 3, INT, INT)
TIMES4 = Function(lambda x: x * 4, INT, INT)
DIV4 = Function(lambda x: x // 4, INT, INT)

GT0 = Function(lambda x: x > 0, INT, BOOL)
LT0 = Function(lambda x: x < 0, INT, BOOL)
EVEN = Function(lambda x: x % 2 == 0, INT, BOOL)
ODD = Function(lambda x: x % 2 == 1, INT, BOOL)

LPLUS = Function(lambda x, y: x + y, (INT, INT), INT)
LMINUS = Function(lambda x, y: x - y, (INT, INT), INT)
LTIMES = Function(lambda x, y: x * y, (INT, INT), INT)
LDIV = Function(lambda x, y: x // y, (INT, INT), INT)
LMIN = Function(min, (INT, INT), INT)
LMAX = Function(max, (INT, INT), INT)

LAMBDA = [PLUS1, MINUS1, TIMES2, DIV2, TIMESNEG1, POW2, TIMES3, DIV3, TIMES4, DIV4, GT0, LT0, EVEN, ODD, LPLUS, LMINUS, LTIMES, LDIV, LMIN, LMAX]

# higher order functions
MAP = Function(lambda f, xs: [f(x) for x in xs], (FunctionType(INT, INT), LIST), INT)
FILTER = Function(lambda f, xs: [x for x in xs if f(x)], (FunctionType(INT, INT), LIST), INT)
COUNT = Function(lambda f, xs: len([x for x in xs if f(x)]), (FunctionType(INT, INT), LIST), INT)
ZIPWITH = Function(lambda f, xs, ys: [f(x, y) for (x, y) in zip(xs, ys)], (FunctionType(INT, INT), LIST, LIST), LIST)

def _scan1l(f, xs):
    ys = []
    for i, x in enumerate(xs):
        if i:
            ys.append(f(ys[-1], x))
        else:
            ys.append(x)
    return ys

SCANL1 = Function(_scan1l, (FunctionType(INT, INT), LIST), LIST)

HIGHERORDER = [MAP, FILTER, COUNT, ZIPWITH, SCANL1]

FUNCTIONS = FIRSTORDER + LAMBDA + HIGHERORDER

TYPEMAP = collections.defaultdict(list)
def _inittypemap():
    for f in FUNCTIONS:
        TYPEMAP[f.input_type].append(f)
_inittypemap()
