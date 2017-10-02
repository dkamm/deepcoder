import unittest

import numpy as np

from deepcoder.dsl import impl
from deepcoder.dsl.types import INT, LIST
from deepcoder.search import dfs, enumerate_programs
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


    def test_enumerate(self):
        used = [impl.MAP, impl.FILTER, impl.COUNT] + [impl.GT0, impl.LT0, impl.EVEN, impl.ODD]
        weights = np.ones(len(used))
        ctx = Context(dict(zip(used, weights)))

        input_types = [LIST]
        T = 1
        programs = enumerate_programs(input_types, T, ctx)
        self.assertEqual(len(programs), 8)

if __name__ == '__main__':
    unittest.main()
