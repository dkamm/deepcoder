import argparse
import numpy as np

from deepcoder.context import Context
from deepcoder.dsl import impl
from deepcoder.dsl.program import prune, Program
from deepcoder.dsl.types import INT, LIST
from deepcoder.search import enumerate_programs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max_nb_inputs', type=int)
    parser.add_argument('--max_t', type=int)
    parser.add_argument('--max_nb_prog', type=int)
    parser.add_argument('--outfile', type=str)
    args = parser.parse_args()

    # program length
    # input output

    ctx = Context(dict(zip(impl.FUNCTIONS, np.ones(len(impl.FUNCTIONS)))))

    programs = set()
    for nb_inputs in range(1, args.max_nb_inputs + 1):
        # input types
        for nb_list in range(nb_inputs + 1):
            input_types = [LIST] * nb_list + [INT] * (nb_inputs - nb_list)
            print('searching for ', input_types)
            programs |= enumerate_programs(tuple(input_types), len(input_types) + args.max_t, ctx, args.max_nb_prog)

    print('Program count: {} (raw enumeration)'.format(len(programs)))

    programs = {prune(x) for x in programs}

    print('Program count: {} (after pruning)'.format(len(programs)))

    programs = sorted(list(set(programs)))

    with open(args.outfile, 'w') as fh:
        for p in sorted(list(programs)):
            fh.write(p.toprefix() + '\n')
    #from IPython import embed; embed()

if __name__ == '__main__':
    main()

