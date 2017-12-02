import collections
import json
import numpy as np

from deepcoder.dsl import impl
from deepcoder.dsl import constants
from deepcoder.nn import encoding
from deepcoder import util
from keras.layers import Input, Dense, Embedding, Flatten
from keras.layers.merge import Average, Concatenate
from keras.models import Model

K = 256 # number of hidden units
#M = 5   # number of input-output pairs per program
#E = 2   # embedding dimension
L = 20  # length of input (TODO: consolidate definitions of this)
#I = 3   # number of inputs

def get_model(I, E, M=5):
    """Returns a compiled model described in Appendix section C.

    Arguments:
        I (int): number of inputs in each program. input count is
            padded to I with null type and vals.
        E (int): embedding dimension
        M (int): number of examples per program. default 5.

    Returns:
        keras.model compiled keras model as described in Appendix
        section C
    """
    embed = Embedding(constants.NULL + 1, E, input_length=1, name='embedding')
    l1 = Dense(K, activation='sigmoid', name='layer1')
    l2 = Dense(K, activation='sigmoid', name='layer2')
    l3 = Dense(K, activation='sigmoid', name='layer3')

    input_layers = []
    concat_layers = []
    for i in range(M):
        # example inputs
        for j in range(I):
            type_input = Input(shape=(2,),
                name=encoding.get_input_typename(i, j))
            val_inputs = []
            for k in range(L):
                val_input = Input(shape=(1,),
                    name=encoding.get_input_valname(i, j, k))
                val_inputs.append(val_input)

            input_layers += [type_input] + val_inputs

            embed_list = [embed(x) for x in val_inputs]
            flattened_list = [Flatten()(x) for x in embed_list]
            concat_layer = Concatenate()([type_input] + flattened_list)
            concat_layers.append(concat_layer)

        # example output
        type_input = Input(shape=(2,),
            name=encoding.get_output_typename(i))
        val_inputs = []
        for j in range(L):
            val_input = Input(shape=(1,),
                name=encoding.get_output_valname(i, j))
            val_inputs.append(val_input)
        
        input_layers += [type_input] + val_inputs

        embed_list = [embed(x) for x in val_inputs]
        flattened_list = [Flatten()(x) for x in embed_list]
        concat_layer = Concatenate()([type_input] + flattened_list)
        concat_layers.append(concat_layer)

    l1_layers = [l1(x) for x in concat_layers]
    l2_layers = [l2(x) for x in l1_layers]
    l3_layers = [l3(x) for x in l2_layers]
    ave = Average()(l3_layers)
    pred = Dense(len(impl.FUNCTIONS), activation='softmax')(ave)

    model = Model(inputs=input_layers, outputs=pred)
    model.compile('adam', 'categorical_crossentropy')
    return model

def load_data(fileobj, nb_inputs):
    y = []
    rows = []
    for line in fileobj:
        data = json.loads(line.rstrip())
        examples = util.decode_examples(data['examples'])
        row = encoding.get_row(examples, nb_inputs, L)
        y.append(data['attribute'])
        rows.append(row)

    # convert
    X = collections.defaultdict(list)
    for row in rows:
        for k, v in row.items():
            X[k].append(v)

    for k, v in X.items():
        X[k] = np.array(v)

    # preprocess
    for k, v in X.items():
        if not k.endswith('type'):
            # keras embedding requires nonnegative ints so we inc
            # by INTMAX.  This is less than NULL which is 513
            v[v < constants.NULL] += constants.INTMAX

    return X, y