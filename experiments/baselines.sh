#!/bin/bash

set -x
set -i

PROG_LENS=(1 2 3 4 5)
#PROG_LENS=(1 2)
MODES=("dfs" "sort-and-add")
GAS=1000000
#GAS=10000000

for PROG_LEN in ${PROG_LENS[*]}; do
    for MODE in ${MODES[*]}; do

        PROBLEM_FILE="programs_T=${PROG_LEN}_test.jsonl"
        RESULT_FILE="T=${PROG_LEN}_mode=${MODE}_predictor=None_gas=${GAS}.h5"

        gsutil cp gs://deepcoder/datasets/$PROBLEM_FILE $PROBLEM_FILE

        python deepcoder/scripts/solve-problems.py \
            --problemfile $PROBLEM_FILE \
            --outfile $RESULT_FILE \
            --T $PROG_LEN \
            --mode $MODE \
            --gas $GAS

        gsutil cp $RESULT_FILE gs://deepcoder/results/$RESULT_FILE
        rm -f $RESULT_FILE $PROBLEM_FILE
    done
done