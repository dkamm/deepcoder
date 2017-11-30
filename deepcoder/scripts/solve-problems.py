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
from deepcoder.nn import encoding
from deepcoder.dsl import impl
from deepcoder.dsl.program import Program

def load_problems(problemfile):
    problems = []
    with open(problemfile) as fh:
        for line in fh:
            problems.append(json.loads(line.rstrip()))
    return problems

def solve_problem(problem, T, mode='dfs', predictor=None, gas=np.inf):
    examples =  encoding.decode_examples(problem['examples'])
    if predictor is None:
        ctx = context.DefaultContext
    else:
        predictor_input = encoding.get_row(examples, 3, 2)
        predictions = predictor.predict(predictor_input)
        scores = dict(zip(predictions, impl.FUNCTIONS))
        ctx = context.Context(scores)
    start = time.time()
    if mode == 'dfs':
        search_func = search.dfs
    elif mode == 'sort-and-add':
        search_func = search.sort_and_add
    else:
        raise ValueError('invalid search mode {}'.format(mode))
    solution, steps_used = search_func(examples, T, ctx)
    end = time.time()
    if solution:
        solution = solution.prefix
    return solution, end - start, steps_used

def solve_problems(problems, T, mode='dfs', predictor=None, gas=np.inf):
    rows = []
    pbar = tqdm.tqdm(total=len(problems))
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futs = [executor.submit(solve_problem, problem, T, mode, predictor, gas) 
                for problem in problems]
        for fut, problem in zip(futs, problems):
            solution, walltime, steps_used = fut.result()
            rows.append({
                'solution': solution,
                'wall_ms': walltime * 1000,
                'nb_steps': steps_used,
                'reference': problem['program'],
            })
            pbar.update(1)
    pbar.close()
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--problemfile', type=str)
    parser.add_argument('--predictorfile', type=str)
    parser.add_argument('--outfile', type=str)
    parser.add_argument('--T', type=int)
    parser.add_argument('--mode', type=str, 
        choices=['dfs', 'sort-and-add'])
    parser.add_argument('--gas', type=int, default=np.inf)
    args = parser.parse_args()

    problems = load_problems(args.problemfile)

    if args.predictorfile:
        import keras
        predictor = keras.models.load_model(args.predictorfile)
    else:
        predictor = None

    rows = solve_problems(problems, args.T, args.mode, predictor)

    df = pd.DataFrame(rows)
    df.to_hdf(args.outfile, 'data')
    
    #nb_solved = len([x for x in rows if x['solution']])
    #print('solved {}/{} ({:.2f}%)'.format(nb_solved, 
    #    len(rows), nb_solved / len(rows) * 100)) 
    #print(df[['wall (ms)', '# steps']].quantile([.2, .4, .6, .8, 1.]))

if __name__ == '__main__':
    main()