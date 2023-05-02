import argparse
import collections
import functools
import concurrent.futures
import time
import json
import numpy as np
import pandas as pd
import tqdm

from deepcoder import context
from deepcoder import search
from deepcoder import util
from deepcoder.nn import model
from deepcoder.dsl import impl
from deepcoder.dsl.program import Program

def solve_problem(problem, T, mode='dfs', gas=np.inf):
    examples = [util.decode_example(x) for x in problem['examples']]
    predictions = problem.get('prediction', np.zeros(len(impl.FUNCTIONS)))
    scores = dict(zip(impl.FUNCTIONS, predictions))
    ctx = context.Context(scores)
    start = time.time()
    if mode == 'dfs':
        search_func = search.dfs
    elif mode == 'sort-and-add':
        search_func = search.sort_and_add
    else:
        raise ValueError('invalid search mode {}'.format(mode))
    solution, steps_used = search_func(examples, T, ctx, gas)
    end = time.time()
    if solution:
        solution = solution.prefix
    return solution, end - start, steps_used

def solve_problems(problems, T, mode='dfs', gas=np.inf):
    rows = []
    pbar = tqdm.tqdm(total=len(problems))
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futs = [executor.submit(solve_problem, problem, T, mode, gas) 
                for problem in problems]
        for fut, problem in zip(futs, problems):
            solution, walltime, steps_used = fut.result()
            rows.append(collections.OrderedDict([
                ('nb_steps', steps_used),
                ('wall_ms', walltime * 1000),
                ('solution', solution),
                ('reference', problem['program']),
            ]))
            pbar.update(1)
    pbar.close()
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('problemfile', type=str)
    parser.add_argument('--predictor', type=str)
    parser.add_argument('--outfile', type=str)
    parser.add_argument('--T', type=int)
    parser.add_argument('--mode', type=str, 
        choices=['dfs', 'sort-and-add'],
        default='dfs')
    parser.add_argument('--gas', type=int, default=np.inf)
    args = parser.parse_args()

    problems = json.loads(open(args.problemfile).read())

    if args.predictor:
        # annotate problems with predictions
        import keras
        predictor = keras.models.load_model(args.predictor)
        max_nb_inputs = model.get_max_nb_inputs(predictor)
        X, _ = model.get_XY(problems, max_nb_inputs)
        predictions = predictor.predict(X)
        for problem, pred in zip(problems, predictions):
            problem['prediction'] = pred

    rows = solve_problems(problems, args.T, args.mode, args.gas)

    df = pd.DataFrame(rows)
    nb_solved = len(df) - sum(df.solution.isnull())
    print('summary:')
    print('solved {}/{} ({}%)'.format(nb_solved, len(df), nb_solved * 100. / len(df)))
    print(df.describe())
    if args.outfile:
        print('saving results to', args.outfile)
        df.to_hdf(args.outfile, 'data')
   
if __name__ == '__main__':
    main()