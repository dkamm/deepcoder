import argparse
import random

import numpy as np
import tqdm

from deepcoder.context import Context
from deepcoder.dsl import constraint
from deepcoder.dsl import impl
from deepcoder.dsl.program import prune, Program
from deepcoder.dsl.types import INT, LIST
from deepcoder.search import enumerate_programs

def get_input_type_combinations(nb_inputs):
    input_type_combinations = []
    for nb_inputs in range(1, nb_inputs + 1):
        # no valid program takes only ints.
        for nb_list in range(1, nb_inputs + 1):
            input_types = [LIST] * nb_list + [INT] * (nb_inputs - nb_list)
            input_type_combinations.append(input_types)
    return input_type_combinations


def is_disjoint(program, others):
    input_output_examples = constraint.get_input_output_examples(program)
    for other in others:
        if constraint.is_same(program, other, input_output_examples):
            return False
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--nb_inputs', type=int)
    parser.add_argument('--nb_train', type=int)
    parser.add_argument('--nb_test', type=int)
    parser.add_argument('--prog_len', type=int)
    parser.add_argument('--outfile', type=str)
    args = parser.parse_args()

    ctx = Context(dict(zip(impl.FUNCTIONS, np.ones(len(impl.FUNCTIONS)))))

    input_type_combinations = get_input_type_combinations(args.nb_inputs)

    programs = enumerate_programs(input_type_combinations, args.prog_len,
        ctx, args.nb_train + args.nb_test)

    # train / test split
    random.shuffle(programs)

    args.nb_test = min(len(programs) / 2, args.nb_test)
    args.nb_train = min(len(programs) - args.nb_test, args.nb_train)

    train_programs = programs[:args.nb_train]
    test_programs = programs[args.nb_train:args.nb_train + args.nb_test]

    # TODO: rethink how to enforce semantic disjoint.
    # Hard to get exactly nb_train/nb_test programs where nb_test is
    # semantic disjoint from train.

    #train_programs = set(programs)
    #test_programs = []
    #pbar = tqdm.tqdm(total=args.nb_test)
    #for program in programs:
    #    # enforce semantically disjoint test set
    #    if (len(test_programs) < args.nb_test and
    #        is_disjoint(program, train_programs - {program})):
    #       test_programs.append(program)
    #       train_programs.discard(program)
    #       pbar.update(1)

    train_outfile = args.outfile.replace('.txt', '') + '_train.txt'
    test_outfile = args.outfile.replace('.txt', '') + '_test.txt'

    for programs, outfile in zip([train_programs, test_programs],
        [train_outfile, test_outfile]):
        print('writing ', outfile)
        with open(outfile, 'w') as fh:
            for program in sorted(list(programs)):
                fh.write(program.prefix + '\n')

if __name__ == '__main__':
    main()

