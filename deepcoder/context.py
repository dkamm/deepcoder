import collections

import numpy as np
from deepcoder.dsl.impl import FUNCTIONS, LAMBDAS

class Context(object):
    def __init__(self, scores_map):
        items = sorted(scores_map.items(), key=lambda x: x[1])
        self._scores_map = scores_map

        self._functions = [f for f, _  in items if f not in LAMBDAS]
        self._typemap = collections.defaultdict(list)
        for f, _ in items:
            self._typemap[f.type].append(f)

    @property
    def typemap(self):
        return self._typemap

    @property
    def functions(self):
        """Returns functions to iterate over in search."""
        return self._functions

DefaultContext = Context(dict(zip(FUNCTIONS, np.ones(len(FUNCTIONS)))))
