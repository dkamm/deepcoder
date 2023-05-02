import collections

from deepcoder.dsl.function import Function
from deepcoder.dsl.types import INT, BOOL, LIST, FunctionType

# firstorder functions
def _head(xs): return xs[0] if xs else None
HEAD = Function('HEAD', _head, LIST, INT)
def _tail(xs): return xs[-1] if xs else None
TAIL = Function('TAIL', _tail, LIST, INT)
def _minimum(xs): return min(xs) if xs else None
MINIMUM = Function('MINIMUM', _minimum, LIST, INT)
def _maximum(xs): return max(xs) if xs else None
MAXIMUM = Function('MAXIMUM', _maximum, LIST, INT)
def _reverse(xs): return xs[::-1]
REVERSE = Function('REVERSE', _reverse, LIST, LIST)
SORT = Function('SORT', sorted, LIST, LIST)
SUM = Function('SUM', sum, LIST, INT)

def _take(n, xs): return xs[:n]
TAKE = Function('TAKE', _take, (INT, LIST), LIST)
def _drop(n, xs): return xs[n:]
DROP = Function('DROP', _drop, (INT, LIST), LIST)
def _access(n, xs): return xs[n] if n >= 0 and len(xs) > n else None
ACCESS = Function('ACCESS', _access, (INT, LIST), INT)


# lambda functions
def _plus1(x): return x + 1
PLUS1 = Function('+1', _plus1, INT, INT)
def _minus1(x): return x - 1
MINUS1 = Function('-1', _minus1, INT, INT)
def _times2(x): return x * 2
TIMES2 = Function('*2', _times2, INT, INT)
def _div2(x): return int(x / 2)
DIV2 = Function('/2', _div2, INT, INT)
def _timesneg1(x): return -x
TIMESNEG1 = Function('*-1', _timesneg1, INT, INT)
def _pow2(x): return x ** 2
POW2 = Function('**2', _pow2, INT, INT)
def _times3(x): return x * 3
TIMES3 = Function('*3', _times3, INT, INT)
def _div3(x): return int(x / 3)
DIV3 = Function('/3', _div3, INT, INT)
def _times4(x): return x * 4
TIMES4 = Function('*4', _times4, INT, INT)
def _div4(x): return int(x / 4)
DIV4 = Function('/4', _div4, INT, INT)

def _gt0(x): return x > 0
GT0 = Function('>0', _gt0, INT, BOOL)
def _lt0(x): return x < 0
LT0 = Function('<0', _lt0, INT, BOOL)
def _even(x): return x % 2 == 0
EVEN = Function('EVEN', _even, INT, BOOL)
def _odd(x): return x % 2 == 1
ODD = Function('ODD', _odd, INT, BOOL)

def _lplus(x, y): return x + y
LPLUS = Function('+', _lplus, (INT, INT), INT)
def _lminus(x, y): return x - y
LMINUS = Function('-', _lminus, (INT, INT), INT)
def _ltimes(x, y): return x * y
LTIMES = Function('*', _ltimes, (INT, INT), INT)
#LDIV = Function('/', lambda x, y: x / y if y else None, (INT, INT), INT)
LMIN = Function('min', min, (INT, INT), INT)
LMAX = Function('max', max, (INT, INT), INT)

# higher order functions
def _map(f, xs): return tuple(f(x) for x in xs)
MAP = Function('MAP', _map, (FunctionType(INT, INT), LIST), LIST)
def _filter(f, xs): return tuple(x for x in xs if f(x))
FILTER = Function('FILTER', _filter, (FunctionType(INT, BOOL), LIST), LIST)
def _count(f, xs): return len(_filter(f, xs))
COUNT = Function('COUNT', _count, (FunctionType(INT, BOOL), LIST), INT)
def _scan1l(f, xs):
    ys = [0] * len(xs)
    for i, x in enumerate(xs):
        if i:
            ys[i] = f(ys[i - 1], x)
        else:
            ys[i] = x
    return tuple(ys)
SCAN1L = Function('SCAN1L', _scan1l, (FunctionType((INT, INT), INT), LIST), LIST)
def _zipwith(f, xs, ys): return tuple(f(x, y) for x, y in zip(xs, ys))
ZIPWITH = Function('ZIPWITH', _zipwith, (FunctionType((INT, INT), INT), LIST, LIST), LIST)

LAMBDAS = [
    PLUS1,
    MINUS1,
    TIMES2,
    DIV2,
    TIMESNEG1,
    POW2,
    TIMES3,
    DIV3,
    TIMES4,
    DIV4,

    GT0,
    LT0,
    EVEN,
    ODD,

    LPLUS,
    LMINUS,
    LTIMES,
    #LDIV,
    LMIN,
    LMAX,
]

FUNCTIONS = [
    HEAD,
    TAIL,
    MINIMUM,
    MAXIMUM,
    REVERSE,
    SORT,
    SUM,

    TAKE,
    DROP,
    ACCESS,

    MAP,
    FILTER,
    COUNT,
    SCAN1L,
    ZIPWITH,
] + LAMBDAS

NAME2FUNC = {x.name : x for x in FUNCTIONS}