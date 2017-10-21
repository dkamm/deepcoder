import numpy as np

from deepcoder.dsl import constants
from deepcoder.dsl.types import INT, LIST
from deepcoder.dsl.value import Value
from deepcoder.dsl import impl

def get_attribute_vec(program):
    # attributes
    y = [0] * len(impl.FUNCTIONS)
    for f, inputs in program.stmts:
        for x in [f] + list(inputs):
            if x in impl.FUNCTIONS:
                y[impl.FUNCTIONS.index(x)] = 1
    return y

def decode_examples(examples):
    new_examples = []
    for inputs, output in examples:
        new_inputs = [Value.construct(x) for x in inputs]
        new_output = Value.construct(output)
        new_examples.append((new_inputs, new_output))
    return new_examples

def encode(value, L):
    if value.type == LIST:
        typ = [0, 1]
        vals = value.val + [constants.NULL] * (L - len(value.val))
    elif value.type == INT:
        typ = [1, 0]
        vals = [value.val] + [constants.NULL] * (L - 1)
    for x in vals:
        if x != constants.NULL and (x > constants.INTMAX or x < constants.INTMIN):
            raise ValueError(str(vals))
    return typ, vals

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


