import argparse
import random

import numpy as np
import tqdm

from deepcoder.context import Context
from deepcoder.dsl import constraint
from deepcoder.dsl import impl
from deepcoder.dsl.function import OutputOutOfRangeError, NullInputError
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
    parser.add_argument('--train_out', type=str)
    parser.add_argument('--test_out', type=str)
    parser.add_argument('--enforce_disjoint', action='store_true')
    args = parser.parse_args()

    ctx = Context(dict(zip(impl.FUNCTIONS, np.ones(len(impl.FUNCTIONS)))))

    input_type_combinations = get_input_type_combinations(args.nb_inputs)

    programs = enumerate_programs(input_type_combinations, args.prog_len,
        ctx, args.nb_train + args.nb_test)

    # train / test split
    random.shuffle(programs)

    args.nb_test = min(len(programs) / 2, args.nb_test)
    args.nb_train = min(len(programs) - args.nb_test, args.nb_train)

    if args.enforce_disjoint:
        train_programs = set(programs)
        test_programs = []
        for program in tqdm.tqdm(programs, total=args.nb_test):
            input_output_examples = None
            for i in range(5):
                try:
                    input_output_examples = constraint.get_input_output_examples(program, M=2)
                except NullInputError:
                    continue

            if not input_output_examples:
                train_programs.discard(program)
                continue

            same_programs = set()
            for train_program in train_programs:
                if constraint.is_same(program, train_program, input_output_examples):
                    same_programs.add(train_program)

            test_programs.append(program)
            train_programs.difference_update(same_programs)

            if len(test_programs) == args.nb_test:
                break
    else:
        train_programs = programs[args.nb_train]
        test_programs = programs[args.nb_train:args.nb_train + args.nb_test]

    train_outfile = args.train_out
    test_outfile = args.test_out

    for programs, outfile in zip([train_programs, test_programs],
        [train_outfile, test_outfile]):
        print('writing ', outfile, '({} programs)'.format(len(programs)))
        with open(outfile, 'w') as fh:
            for program in sorted(list(programs)):
                fh.write(program.prefix + '\n')

if __name__ == '__main__':
    main()

