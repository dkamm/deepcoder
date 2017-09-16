import collections
import itertools

from deepcoder.dsl.constants import NULL
from deepcoder.dsl.variable import Variable
from deepcoder.dsl import types

def iterate_inputs(f, typemap):
    """Yields the cartesian product over valid inputs for f according to typemap.

    Args:
        f: Function to get inputs for
        typemap: type -> list of Function or Variable
    """
    argslists = []
    for input_type in f.type.input_types:
        argslists.append(typemap[input_type])
    for args in itertools.product(*argslists):
        yield args

def dfs(inputs, output, T, ctx):
    """Runs dfs search up to depth T or until a program is found that matches output.
    Args:
        inputs: list of int or list
        output: int or list
        T: max depth
        ctx: Context. used to restrict/order the set of functions that dfs searches over.

    Returns:
        tuple of valid and prefixmap
    """

    input_variables = []
    for i, input in enumerate(inputs):
        if isinstance(input, list):
            typ = types.LIST
        elif isinstance(input, int):
            typ = types.INT
        else:
            raise TypeError('input must be str or list, got {}'.format(type(input)))
        input_variables.append(Variable(str(i), input, typ))

    prefixmap = {}
    valid = []

    # init
    prefix = ''
    for i, x in enumerate(input_variables):
        if i:
            prefix += '|'
        prefix += str(x.type)
        prefixmap[prefix] = x

    def dfshelper(baseprefix, t):
        if prefixmap[baseprefix].x == output:
            valid.append(baseprefix)
            return True

        if t == T:
            return

        typemap = collections.defaultdict(list)

        stms = baseprefix.rstrip('|').split('|')
        prefix = ''
        used = set()
        for i, stm in enumerate(stms):
            if i:
                prefix += '|'
            prefix += stm
            v = prefixmap[prefix]
            used.add(stm) # INT and LIST are added but won't be used
            typemap[v.type].append(v)
        typemap.update(ctx.typemap)

        for f in ctx.functions:
            for args in iterate_inputs(f, typemap):

                stm = f.name + ',' + ','.join([x.name for x in args])
                if stm in used:
                    continue
                raw_args = [x.x for x in args]
                y = f(*raw_args)
                if y == NULL:
                    # throw out null results
                    continue
                prefix = baseprefix + '|' + stm
                prefixmap[prefix] = Variable(str(t + len(inputs)), y, f.output_type)
                if dfshelper(prefix, t + 1):
                    return True

    dfshelper(prefix, 0)
    return valid, prefixmap

def search_and_add():
    pass

