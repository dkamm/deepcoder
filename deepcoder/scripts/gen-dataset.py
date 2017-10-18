
import argparse
import collections

import numpy as np
import tqdm

from deepcoder.dsl import constants
from deepcoder.dsl import constraint
from deepcoder.dsl import impl
from deepcoder.dsl.program import Program, gen_inputs
from deepcoder.dsl.types import INT, LIST

def encode(variable):
    if variable.type == LIST:
        typ = [0, 1]
        vals = variable.val + [constants.NULL] * (constraint.L - len(variable.val))
    elif variable.type == INT:
        typ = [1, 0]
        vals = [variable.val] + [constants.NULL] * (constraint.L - 1)
    for x in vals:
        if x != constants.NULL and (x > constants.INTMAX or x < constants.INTMIN):
            raise ValueError(str(vals))
    return typ, vals

def get_attribute_vec(program):
    # attributes
    y = np.zeros(len(impl.FUNCTIONS))
    for f, inputs in program.stmts:
        for x in [f] + list(inputs):
            if x in impl.FUNCTIONS:
                y[impl.FUNCTIONS.index(x)] = 1
    return y

def get_program_row(program, M, nb_inputs):
    row = {}
    program_examples = constraint.get_input_output_examples(
        program, M)

    def get_input_prefix(example_idx, input_idx):
        # tensorflow complained about either = or _ in names
        return 'example{}input{}'.format(example_idx, input_idx)

    for i, (inputs, output) in enumerate(program_examples):
        for j, input in enumerate(inputs):
            typ, vals = encode(input)
            row[get_input_prefix(i, j) + 'type'] = typ
            row[get_input_prefix(i, j) + 'vals'] = vals

        for j in range(len(inputs), nb_inputs):
            # pad with null
            typ = [0, 0]
            vals = [constants.NULL] * constraint.L
            row[get_input_prefix(i, j) + 'type'] = typ
            row[get_input_prefix(i, j) + 'vals'] = vals

        typ, vals = encode(output)
        row['example{}outputtype'.format(i)] = typ
        row['example{}outputvals'.format(i)] = vals

    return row

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', type=str)
    parser.add_argument('--outfile', type=str)
    parser.add_argument('--nb_examples', type=int, default=5)
    parser.add_argument('--nb_inputs', type=int, default=3)
    args = parser.parse_args()

    with open(args.infile) as in_fh:
        line_count = sum([1 for _ in in_fh])

    with open(args.infile) as in_fh:
        xdata = []
        ydata = []
        programs = []
        pbar = tqdm.tqdm(total=line_count)
        for line in in_fh:
            pbar.update(1)
            program = Program.parse(line.rstrip())
            try:
                xdata.append(get_program_row(program,
                                             args.nb_examples,
                                             args.nb_inputs))
                ydata.append(get_attribute_vec(program))
            except:
                print('prog:', program)
                print('constraint:')
                for x in constraint.propagate_constraints(program):
                    print(x)
                raise
            programs.append(program)

    x = collections.defaultdict(list)
    for row in xdata:
        for k, v in row.items():
            x[k].append(v)
    np.savez(args.outfile, y=ydata, **x)

if __name__ == '__main__':
    main()
