import argparse
import numpy as np

from deepcoder.context import Context
from deepcoder.dsl import impl
from deepcoder.dsl.program import prune, Program
from deepcoder.dsl.types import INT, LIST
from deepcoder.search import enumerate_programs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('maxdepth', type=int)
    parser.add_argument('maxprog', type=int)
    args = parser.parse_args()

    # program length
    # input output

    ctx = Context(dict(zip(impl.FUNCTIONS, np.ones(len(impl.FUNCTIONS)))))

    programs = set()
    for i in range(args.maxdepth - 1):
        # input types
        input_types = []
        for j in range(i):
            input_types.append(LIST)
        for j in range(len(input_types), i):
            input_types.append(INT)

        programs |= enumerate_programs(tuple(input_types), args.maxdepth, ctx, args.maxprog)

    print('Program count: {} (raw enumeration)'.format(len(programs)))

    programs = {prune(x) for x in programs}

    print('Program count: {} (after pruning)'.format(len(programs)))

    programs = sorted(list(set(programs)))

    from IPython import embed; embed()

if __name__ == '__main__':
    main()

