import argparse
import json
import tqdm

from deepcoder.dsl import constraint
from deepcoder.dsl.function import NullInputError
from deepcoder.dsl.program import Program
from deepcoder import util

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', type=str)
    parser.add_argument('--outfile', type=str)
    parser.add_argument('--nb_examples', type=int, default=5)
    args = parser.parse_args()

    with open(args.infile) as in_fh:
        programs = [Program.parse(l.rstrip()) for l in in_fh]

    problems = []
    for program in tqdm.tqdm(programs, total=len(programs)):
        problem = {}
        examples = None
        # only try twice for speed
        for _ in range(2):
            try:
                examples = constraint.get_input_output_examples(program, args.nb_examples)
            # TODO: figure out why OutputOutOfRange happened here in T=4 generation
            except (NullInputError, constraint.InvalidConstraintError, constraint.OutputOutOfRangeError):
                continue
        if not examples:
            continue
        raw_examples = []
        for inputs, output in examples:
            raw_inputs = [x.val for x in inputs]
            raw_output = output.val
            raw_examples.append(dict(inputs=raw_inputs, output=raw_output))
        problem = dict(program=program.prefix, examples=raw_examples,
            attribute=util.get_attribute_vec(program))
        problems.append(problem)

    with open(args.outfile, 'w') as out_fh:
        print('[', file=out_fh)
        for i, problem in enumerate(problems):
            trailing_comma = i < len(problems) - 1
            util.pretty_print_problem(problem, out_fh, trailing_comma)
        print(']', file=out_fh)

if __name__ == '__main__':
    main()

