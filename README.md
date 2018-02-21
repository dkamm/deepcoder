# Deepcoder
Pure python 3 implementation of DeepCoder (https://arxiv.org/pdf/1611.01989.pdf)

# Usage
## quickstart
1. Install requirements
```
pip install -r requirements.txt
```

2. Download dataset
```
wget https://storage.googleapis.com/deepcoder/dataset.tar.gz
tar xvf dataset.tar.gz # extracts to folder dataset
```

3. Run solver
```
python -m deepcoder.scripts.solve-problems dataset/T=2_test.json --T 2 --mode dfs --gas 1000

100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 100/100 [00:00<00:00, 147.26it/s]
summary:
solved 53/100 (53.0%)
          nb_steps     wall_ms
count   100.000000  100.000000
mean    628.420000   50.401287
std     412.020181   32.888645
min       1.000000    0.053883
25%     175.500000   15.448511
50%     830.000000   70.028543
75%    1000.000000   77.140987
max    1002.000000  102.509022
```
(gas is a limit on the number of nodes explored per problem)

4. Train neural net
```
python -m deepcoder.scripts.train-nn --in dataset/T=2_train.json --out model.h5 --epochs 10
```

5. Run solver with neural net
```
python -m deepcoder.scripts.solve-problems dataset/T=2_test.json --T 2 --mode dfs --gas 1000 --predictor model.h5

100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 100/100 [00:00<00:00, 175.35it/s]
summary:
solved 68/100 (68.0%)
          nb_steps     wall_ms
count   100.000000  100.000000
mean    475.280000   41.453178
std     409.670626   35.350695
min       1.000000    0.050783
25%      69.000000    6.203175
50%     389.000000   31.166434
75%    1000.000000   78.977406
max    1003.000000  102.050066
```

## data generation

Dataset format:
```
[
{
        "program": "LIST|LIST|COUNT,>0,0|ZIPWITH,+,1,0|ACCESS,2,3",
        "examples": [
                {
                        "inputs": [
                                [-46, -23, -78, 10],
                                [125, 105, -69]
                        ],
                        "output": 82
                },
                {
                        "inputs": [
                                [90, 103, -57, 13, -45, 28, -30, 68, -113, 60, -71, 48, -117, 79, -42, -43, 37, -96],
                                [13, -52, 48, 6, -8, -55, 35, 75]
                        ],
                        "output": null
                },
                ...
        ],
        "attribute": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0]
},
...
]
```
(borrowed from HiroakiMikami and should be compatible). each dataset file is valid json and directly loadable like `json.loads(open('dataset_file.json').read())`

### generate paper's datasets
To generate datasets used in the paper, use this script. Note it will take a long time (~1d). Also dataset.tar.gz was generated from this script.
```
./deepcoder/scripts/gen-datasets.sh
```

### generate programs
```
python -m deepcoder.scripts.gen-programs \
    --nb_inputs $NB_INPUTS --nb_train $NB_TRAIN --nb_test $NB_TEST \
    --prog_len $PROG_LEN --train_out $TRAIN_PROG --test_out $TEST_PROG \
    --enforce_disjoint
```
Enforcing semantic disjoint will increase the runtime substantially.


### generate problems from programs
```
python deepcoder.scripts.gen-problems --infile $PROGRAM_FILE \
    --outfile $PROBLEM_FILE
```
Because the constraint propagation is not perfect, some amount of resampling must be done so generating examples for each problem takes a long time.

## tests
```
python -m unittest
```

# Notes
- [-256,256] is the int range like in the paper. `null` is 513 
- embedding vector encodes int range as [1,514]
- model construction uses keras dict input functionality heavily (see nn/encoding.py)
- caching intermediate results by prefix optimization is not implemented
- performance is much slower than what they reported. this explores about 10k nodes/s and is about 100x slower than theirs. solving all T=3 test problems takes about 10^6 steps -> 100s vs 1s they reported. authors had a c++ implementation with intermediate result caching which may account for speed difference

## terminology
- problem: a set of input, output examples for a program
- gas: an optional limit on the max number of nodes explored in a search while solving a *single* problem (term inspired by ethereum)


## constraint propagation
The constraint propagation code is hairy and I have not yet figured out all the cases. The paper doesn't provide much detail on this part.

In this implementation, each list constraint has a range of possible lengths and an integer range constraint for each possible length. This makes it possible to have a more accurate constraint for SCAN1L.  For instance, for SCAN1L with *, the constraint is [-log 256/L, log 256/L] where L is the length of the list.

The paper does not specify how to handle ACCESS with a null input. It can arise in a program such as this `LIST|FILTER,>0,0|ACCESS,0,2`. What seems right is to find constraints such that ACCESS with a null argument never happens. I think it can be done by attaching a set of constraints like (>0,even) and (<0,odd) to each length slot in the list constraint but it's tricky.

For example, consider the (long) program
```
a <- List
b <- Filter(>0, a)
c <- Filter(even,b)
d <- Filter(<0, a)
e <- Filter(odd, d)
f <- Head(c)
g <- Head(e)
h <- Access(f,a)
i <- Access(g,a)
```
The Access statements would propagate (>0,even) and (<0,odd) to the list constraint for `a` and this would restrict the list length to >=2. However, the Head calls also impose an integer range constraint where each element must be in [0,L-1] where L is the candidate length of the list- this violates the (<0,odd) constraint on `a` so we should throw the program out.

As of now, example generation samples a few times and just throws out examples that yield out of bounds or null input errors.

## program representation
Programs in the deepcoder dsl can be completely specified by a string format that is easily parsed.
```
| delimits each statement
, delimits a function call and its arguments
```

The general format is
```
INPUT_0_TYPE|...|INPUT_K_TYPE|FUNCTION_CALL_0|...|FUNCTION_CALL_N
```
Types of each statement are recoverable since we know the output type of each function.

As an example, consider the program
```
a <- [1,2,3,4]
b <- 5
c <- f(a)
d <- g(b)
e <- h(c, d)
```

This would be encoded as

```
LIST|INT|f,0|g,1|h,2,3
```
