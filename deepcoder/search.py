import collections
import itertools

import tqdm

from deepcoder.dsl.constants import NULL
from deepcoder.dsl.variable import Variable
from deepcoder.dsl import types
from deepcoder.dsl.program import Program

def iterate_inputs(f, typemap):
    """Yields the cartesian product over valid inputs for f according to typemap.

    Args:
        f: Function to get inputs for
        typemap: type -> list of Function or Variable
    Yields:
        Tuple of mixed types (Variable or Function) representing arguments to f
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

    # init
    inputtypemap = collections.defaultdict(list)
    prefixmap = {}
    for i, x in enumerate(input_variables):
        input_types = [x.type for x in input_variables[:i+1]]
        p_base = Program(input_types, tuple())
        prefixmap[p_base] = x
        inputtypemap[x.type].append(x)
    valid = []

    def dfshelper(p_base, t):
        if prefixmap[p_base].x == output:
            valid.append(p_base)
            return True

        if t == T:
            return

        typemap = collections.defaultdict(list)
        for k, v in inputtypemap.items():
            typemap[k] += v

        used = set()
        for i, stmt in enumerate(p_base.stmts):
            p = Program(p_base.input_types, p_base.stmts[:i+1])
            v = prefixmap[p]
            used.add(stmt)
            if v.x != NULL:
                # don't consider NULL for input iteration
                typemap[v.type].append(v)

        for k, v in ctx.typemap.items():
            typemap[k] += v

        for f in ctx.functions:
            for args in iterate_inputs(f, typemap):
                stmt = (f, args)
                if stmt in used:
                    continue
                raw_args = [x.x for x in args]
                y = f(*raw_args)
                #if y == NULL:
                #    # throw out null results
                #    continue
                p = Program(p_base.input_types, list(p_base.stmts) + [stmt])
                prefixmap[p] = Variable(str(t + len(inputs)), y, f.output_type)
                if dfshelper(p, t + 1):
                    return True

    dfshelper(p_base, 0)
    return valid, prefixmap

def enumerate_programs(input_types, T, ctx, limit=None):
    programs = set()
    p_base = Program(input_types, [])

    pbar = tqdm.tqdm(total=limit)

    def helper(p_base, t):
        if t == T:
            return

        typemap = collections.defaultdict(list)
        for i, typ in enumerate(p_base.types):
            typemap[typ].append(i)

        for k, v in ctx.typemap.items():
            typemap[k] += v

        used = set(p_base.stmts)
        for f in ctx.functions:
            for args in iterate_inputs(f, typemap):

                stmt = f, args
                if stmt in used:
                    continue

                p = Program(p_base.input_types, list(p_base.stmts) + [stmt])
                programs.add(p)
                pbar.update(1)
                if limit and len(programs) >= limit:
                    return
                helper(p, t + 1)

    helper(p_base, 0)
    pbar.close()
    return programs


def search_and_add():
    # TODO
    pass

