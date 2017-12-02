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

def decode_examples(raw_examples):
    examples = []
    for raw_inputs, raw_output in raw_examples:
        inputs = [Value.construct(x) for x in raw_inputs]
        output = Value.construct(raw_output)
        examples.append((inputs, output))
    return examples
