import numpy as np

from deepcoder.dsl import constants
from deepcoder.dsl.types import INT, LIST
from deepcoder.dsl.value import NULLVALUE

L = 20  # length of input 

def encode(value, L=L):
    if value.type == LIST:
        typ = [0, 1]
        vals = value.val + [constants.NULL] * (L - len(value.val))
    elif value.type == INT:
        typ = [1, 0]
        vals = [value.val] + [constants.NULL] * (L - 1)
    elif value == NULLVALUE:
        typ = [0, 0]
        vals = [constants.NULL] * L
    return typ, vals

def get_input_prefix(example_idx, input_idx):
    # tensorflow complained about either = or _ in names
    return 'example{}input{}'.format(example_idx, input_idx)

def get_input_typename(example_idx, input_idx):
    return get_input_prefix(example_idx, input_idx) + 'type'

def get_input_valname(example_idx, input_idx, val_idx):
    return get_input_prefix(example_idx, input_idx) + 'val' + str(val_idx)

def get_output_prefix(example_idx):
    return 'example{}output'.format(example_idx)

def get_output_typename(example_idx):
    return get_output_prefix(example_idx) + 'type'

def get_output_valname(example_idx, val_idx):
    return get_output_prefix(example_idx) + 'val' + str(val_idx)

def get_row(examples, max_nb_inputs, L=L):
    row = {}
    for i, (inputs, output) in enumerate(examples):
        for j, input in enumerate(inputs):
            typ, vals = encode(input, L)
            row[get_input_typename(i, j)] = typ
            for k, val in enumerate(vals):
                row[get_input_valname(i, j, k)] = val

        for j in range(len(inputs), max_nb_inputs):
            # pad with null
            typ, vals = encode(NULLVALUE, L)
            row[get_input_typename(i, j)] = typ
            for k, val in enumerate(vals):
                row[get_input_valname(i, j, k)] = val

        typ, vals = encode(output, L)
        row[get_output_typename(i)] = typ
        for j, val in enumerate(vals):
            row[get_output_valname(i, j)] = val
    return row