import unittest

import numpy as np

from deepcoder.dsl import impl
from deepcoder.search import dfs
from deepcoder.context import Context

class TestSearch(unittest.TestCase):
    def test_dfs(self):
        ctx = Context(dict(zip(impl.FUNCTIONS, np.ones(len(impl.FUNCTIONS)))))

        inputs = [[1,2,3,4,5]]
        output = [2,4,6,8,10]

        T = 2
        valid, prefixmap = dfs(inputs, output, T, ctx)
        self.assertTrue(valid)
        self.assertTrue(len(prefixmap))


    def test_impossible(self):
        """Return the first n primes which is impossible in this language."""
        ctx = Context(dict(zip(impl.FUNCTIONS, np.ones(len(impl.FUNCTIONS)))))

        inputs = [list(range(6))]
        output = [2,3,5,7,11,13]

        T = 2
        valid, prefixmap = dfs(inputs, output, T, ctx)
        self.assertFalse(valid)
        self.assertTrue(len(prefixmap) > 2000)


if __name__ == '__main__':
    unittest.main()
