import collections
import concurrent.futures
import copy
import itertools
import multiprocessing
import queue
import time

import numpy as np

import tqdm

from deepcoder import context
from deepcoder.dsl.value import IntValue, NULLVALUE
from deepcoder.dsl import types
from deepcoder.dsl.function import OutputOutOfRangeError, NullInputError
from deepcoder.dsl.program import Program, get_unused_indices

def iterate_inputs(f, type_to_inputs):
    """Yields the cartesian product over valid inputs for f according to type_to_inputs.

    Args:
        f: Function to get inputs for
        type_to_inputs: type -> list of Value
    Yields:
        Tuple of mixed types (Variable or Function) representing arguments to f
    """
    argslists = []
    for input_type in f.type.input_types:
        argslists.append(type_to_inputs[input_type])
    for args in itertools.product(*argslists):
        yield args

def is_solution(program, examples):
    for inputs, output in examples:
        if program(*inputs) != output:
            return False
    return True

def has_null(program, examples):
    for inputs, _ in examples:
        if program(*inputs) == NULLVALUE:
            return True
    return False

def dfs(examples, T, ctx, gas=np.inf):
    """Runs dfs search up to depth T or until a program is found that matches output.
    Args:
        examples: list of tuples of (inputs, output)
        T: max depth
        ctx: Context. used to restrict/order the set of functions that dfs searches over.
        gas (int): limit on number of node expansions. default to np.inf (unlimited)

    Returns:
        tuple of solution program, number of steps
    """
    ns = { 'nb_steps': 0,
           'solution': None,
           'gas' : gas }

    # init
    input_types = [x.type for x in examples[0][0]]
    input_type_to_inputs = collections.defaultdict(list)
    for i, input_type in enumerate(input_types):
        input_type_to_inputs[input_type].append(i)
    p_base = Program(input_types, tuple())

    def dfshelper(p_base, t):
        ns['nb_steps'] += 1
        ns['gas'] -= 1
        try:
            if is_solution(p_base, examples):
                ns['solution'] = p_base
                return True
        except (NullInputError, OutputOutOfRangeError):
            # throw out programs that have null inputs or any out of range output
            # null outputs ok if unused
            return

        if ns['gas'] <= 0:
            return True

        if t == T:
            return

        # type -> list of input indices / Functions
        type_to_inputs = collections.defaultdict(list)
        for k, v in input_type_to_inputs.items():
            type_to_inputs[k] += v

        used = set()
        for i, stmt in enumerate(p_base.stmts):
            program = Program(p_base.input_types, p_base.stmts[:i+1])
            used.add(stmt)
            # favor more recent statements
            output_type = stmt[0].output_type
            type_to_inputs[output_type].insert(0, (len(p_base.input_types) + i))

        for k, v in ctx.typemap.items():
            type_to_inputs[k] += v

        for f in ctx.functions:
            for args in iterate_inputs(f, type_to_inputs):
                stmt = (f, args)
                if stmt in used:
                    continue
                program = Program(p_base.input_types, list(p_base.stmts) + [stmt])

                try:
                    if t + 1 < T and has_null(program, examples):
                        continue
                except OutputOutOfRangeError:
                    continue

                if dfshelper(program, t + 1):
                    return True

    dfshelper(p_base, 0)
    return ns['solution'], ns['nb_steps']

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

        type_to_inputs = collections.defaultdict(list)
        for i, typ in enumerate(program_base.types):
            type_to_inputs[typ].append(i)

        for k, v in ctx.typemap.items():
            type_to_inputs[k] += v

        used = set(program_base.stmts)
        for f in ctx.functions:
            for args in iterate_inputs(f, type_to_inputs):

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

    with tqdm.tqdm(total=max_nb_programs) as pbar:
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


def generate_contexts(final_ctx):
    scores_map = {}
    score = 0

    def _get_nearest_partner(f):
        """Returns the partner function to f with the highest score.
        If f is lambda, partner must be a regular function.
        If f is a function and takes lambda as first argument,
        partner is a lambda.
        A function that doesn't take any lambdas is its own patner.

        There are no functions in dsl that take multiple lambdas or a lambda that is not the first argument.

        Arguments:
            f (Function): function to find partner for.

        Returns:
            Function or None. None is if there is no valid partner.
        """
        if f in final_ctx.functions:
            input_type = f.type.input_types[0]
            if not isinstance(input_type, types.FunctionType):
                return f
            if (input_type in final_ctx.typemap and
                final_ctx.typemap[input_type]):
                return final_ctx.typemap[input_type][0]
        else:
            for partner in final_ctx.functions:
                if partner.type.input_types[0] == f.type:
                    return partner

    partners = [_get_nearest_partner(x) for x, _ in final_ctx.items]

    for i, (f, score) in enumerate(final_ctx.items):
        partner = partners[i]
        if not partner or f in scores_map:
            continue

        scores_map[f] = score

        if partner not in scores_map:
            partner_score = final_ctx.scores_map[partner]
            scores_map[partner] = partner_score

        yield context.Context(copy.copy(scores_map))

def sort_and_add(examples, T, final_ctx, gas=np.inf):
    solution = None
    nb_steps_list = []
    for ctx in generate_contexts(final_ctx):
        solution, nb_steps = dfs(examples, T, ctx, gas)
        nb_steps_list.append(nb_steps)
        if solution:
            break
    return solution, nb_steps_list