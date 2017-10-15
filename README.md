## Deepcoder
Pure python 3 implementation of DeepCoder (https://arxiv.org/pdf/1611.01989.pdf)

## Installation
```
pip install -r requirements.txt
```

## Data generation
```
python -m deepcoder.scripts.gen-programs --nb_inputs 3 --max_prog_len 2 --max_nb_prog 100000 --out deepcoder/dataset/programs_small.txt

python -m deepcoder.scripts.gen-dataset --infile deepcoder/dataset/programs_small.txt --outfile deepcoder/dataset/programs_small.npz --nb_examples 5
```

## Tests
```
python -m unittest
```

## Implementation details

### Representation
Programs in the deepcoder dsl can be completely specified by a string format.

| delimits each statement
, delimits a function call and its arguments

The general format is
```
INPUT_0_TYPE|...|INPUT_K_TYPE|FUNCTION_CALL_0|...|FUNCTION_CALL_N
```
Types of each statement are recoverable since we know the output type of each function.

As an example, consider the program

a = [1,2,3,4]
b = 5
c = f(a)
d = g(b)
e = h(c, d)

This would be encoded as
```
LIST|INT|f,0|g,1|h,2,3
```

The map of prefix to result (used in dfs) would look like so:
```
LIST -> [1,2,3,4]
LIST|INT -> 5
LIST|INT|f,0 -> c
LIST|INT|f,0|g,1 -> d
LIST|INT|f,0|g,1|h,2,3 -> e
```
