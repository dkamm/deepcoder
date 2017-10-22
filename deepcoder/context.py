import collections

import numpy as np
from deepcoder.dsl.impl import FUNCTIONS, LAMBDAS

class Context(object):
    def __init__(self, scores_map):
        self.items = sorted(scores_map.items(), key=lambda x: -x[1]) # descending
        self.scores_map = scores_map

        self.functions = [f for f, _  in self.items if f not in LAMBDAS]
        self.typemap = collections.defaultdict(list)
        for f, _ in self.items:
            self.typemap[f.type].append(f)

DefaultContext = Context(dict(zip(FUNCTIONS, np.ones(len(FUNCTIONS)))))
