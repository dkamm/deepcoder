import argparse
import functools
import concurrent.futures
import time
import json
import numpy as np
import pandas as pd
import tqdm

from deepcoder.attribute import get_scores, print_scores
from deepcoder import context
from deepcoder import converter
from deepcoder import search
from deepcoder.dsl import impl
from deepcoder.dsl.program import Program

def solve_sample(sample, T):
    ctx = context.DefaultContext
    program_examples = converter.decode_examples(sample['examples'])
    start = time.time()
    solution, steps_used = search.dfs(program_examples, T, ctx)
    end = time.time()
    if solution:
        solution = solution.prefix
    return solution, end - start, steps_used

def solve_samples(samples, T):
    rows = []
    pbar = tqdm.tqdm(total=len(samples))
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for solution, walltime, steps_used in enumerate(executor.map(solve_sample, samples, [T] * len(samples))):
            rows.append({
                'solution': solution,
                'wall (ms)': walltime * 1000,
                '# steps': steps_used
            })
            pbar.update(1)
    pbar.close()
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', type=str)
    parser.add_argument('--T', type=int)
    parser.add_argument('--predictor', type=str)
    args = parser.parse_args()

    samples = []
    with open(args.samples) as fh:
        for line in fh:
            samples.append(json.loads(line.rstrip()))
    rows = solve_samples(samples, args.T)
    df = pd.DataFrame(rows)
    nb_solved = len([x for x in rows if x['solution']])
    print('solved {}/{} ({:.2f}%)'.format(nb_solved, 
        len(rows), nb_solved / len(rows) * 100)) 
    print(df[['wall (ms)', '# steps']].quantile([.2, .4, .6, .8, 1.]))

if __name__ == '__main__':
    main()