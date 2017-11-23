import argparse
import json
import tqdm

from deepcoder.dsl import constraint
from deepcoder.dsl.function import NullInputError
from deepcoder.dsl.program import Program
from deepcoder import converter

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', type=str)
    parser.add_argument('--outfile', type=str)
    parser.add_argument('--nb_examples', type=int, default=5)
    args = parser.parse_args()

    with open(args.infile) as in_fh:
        programs = [Program.parse(l.rstrip()) for l in in_fh]

    datas = []
    for program in tqdm.tqdm(programs, total=len(programs)):
        data = {}
        examples = None
        for _ in range(2):
            try:
                examples = constraint.get_input_output_examples(program, args.nb_examples)
            except (NullInputError, constraint.InvalidConstraintError):
                continue
        if not examples:
            continue
        raw_examples = []
        for inputs, output in examples:
            raw_inputs = [x.val for x in inputs]
            raw_output = output.val
            raw_examples.append((raw_inputs, raw_output))

        data = dict(program=program.prefix, examples=raw_examples,
            attribute=converter.get_attribute_vec(program))
        datas.append(data)

    with open(args.outfile, 'w') as out_fh:
        for data in datas:
            out_fh.write(json.dumps(data) + '\n')

if __name__ == '__main__':
    main()