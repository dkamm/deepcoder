#!/bin/bash
set -x
set -e

PROG_LENS=(1 2 3 4 5)
NB_TRAINS=(1000000 1000000 5000000 5000000 0)
NB_TESTS=(100 100 500 100 100)
NB_INPUTS=3

for idx in ${!PROG_LENS[*]} ; do
    PROG_LEN=${PROG_LENS[$idx]}
    NB_TRAIN=${NB_TRAINS[$idx]}
    NB_TEST=${NB_TESTS[$idx]}

    echo "Generating programs T=${PROG_LEN} #train=${NB_TRAIN} #test=${NB_TEST}"

    OUT_PREFIX="T=${PROG_LEN}"

    TRAIN_PROG="${OUT_PREFIX}_train_programs.txt"
    TEST_PROG="${OUT_PREFIX}_test_programs.txt"

    TRAIN_OUT="${OUT_PREFIX}_train.json"
    TEST_OUT="${OUT_PREFIX}_test.json"

    python -m deepcoder.scripts.gen-programs \
        --nb_inputs $NB_INPUTS --nb_train $NB_TRAIN --nb_test $NB_TEST \
        --prog_len $PROG_LEN --train_out $TRAIN_PROG --test_out $TEST_PROG \
        --enforce_disjoint

    echo "Generating train problems #train=${NB_TRAIN}"
    python -m deepcoder.scripts.gen-problems --infile $TRAIN_PROG \
        --outfile $TRAIN_OUT

    echo "Generating test problems #test=${NB_TEST}"
    python -m deepcoder.scripts.gen-problems --infile $TEST_PROG \
        --outfile $TEST_OUT

    rm -f $TRAIN_PROG
    rm -f $TEST_PROG

done
