import collections
import concurrent.futures
import itertools
import multiprocessing
import queue
import time

import tqdm

from deepcoder.dsl.constants import NULL
from deepcoder.dsl.variable import Variable
from deepcoder.dsl import types
from deepcoder.dsl.program import Program, get_unused_indices

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

def enumerate_helper(input_types, T, ctx, result_queue, stop_queue):
    program_base = Program(input_types, [])

    monitor = {'stopped': False}

    def helper(program_base, t):
        if monitor['stopped']:
            return

        try:
            stop_queue.get_nowait()
            monitor['stopped'] = True
            return
        except queue.Empty:
            pass

        if t == T:
            if not get_unused_indices(program_base):
                result_queue.put(program_base.prefix)
            # don't keep searching if pruned
            # has < T stmts. will get picked up
            # on another enumeration
            return

        typemap = collections.defaultdict(list)
        for i, typ in enumerate(program_base.types):
            typemap[typ].append(i)

        for k, v in ctx.typemap.items():
            typemap[k] += v

        used = set(program_base.stmts)
        for f in ctx.functions:
            for args in iterate_inputs(f, typemap):

                stmt = f, args
                if stmt in used:
                    continue

                program = Program(program_base.input_types,
                    list(program_base.stmts) + [stmt])
                helper(program, t + 1)

    helper(program_base, 0)
    result_queue.put(None) # done
    if not monitor['stopped']:
        stop_queue.get()

def enumerate_programs(input_type_combinations, T, ctx, max_nb_programs):
    """Enumerates programs with T statements that have the same input types.

    Each program is pruned and doesn't have any unused inputs or statements.

    Arguments:
        input_type_combinations (list): list of list of INT or LIST specifying all input types
            to search over
        T (int): number of statements in each outputted program
        ctx (Context): search context
        max_nb_programs (int): max number of programs to enumerate.

    Returns:
        set of programs with input types input_types and exactly T stmts.
    """
    programs = []

    workers = []

    result_queue = multiprocessing.Queue()
    stop_queue = multiprocessing.Queue()

    for input_types in input_type_combinations:
        worker = multiprocessing.Process(target=enumerate_helper,
            args=(input_types, T, ctx, result_queue, stop_queue))
        worker.start()
        workers.append(worker)

    def join():
        for worker in workers:
            worker.join()

    finished_cnt = 0
    def all_done():
        return finished_cnt == len(workers)

    def stop_workers():
        for _ in range(len(workers)):
            stop_queue.put(1)

    def wait_for_workers():
        while True:
            if not sum([worker.is_alive() for worker in workers]):
                return
            time.sleep(.1)

    pbar = tqdm.tqdm(total=max_nb_programs)

    stopped = False
    while not all_done():
        if not stopped and len(programs) >= max_nb_programs:
            stopped = True
            stop_workers()

        try:
            result = result_queue.get_nowait()
            if result is None:
                finished_cnt += 1
                continue

            program = Program.parse(result)
            if len(programs) < max_nb_programs:
                programs.append(program)
                pbar.update(1)
        except queue.Empty:
            continue
    if not stopped:
        stop_workers()
    join()
    return programs

def search_and_add():
    # TODO
    pass

