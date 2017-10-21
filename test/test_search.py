import unittest

import numpy as np

from deepcoder.dsl import impl
from deepcoder.dsl.types import INT, LIST
from deepcoder.dsl.value import IntValue, ListValue
from deepcoder.search import dfs, enumerate_programs
from deepcoder.context import Context

class TestSearch(unittest.TestCase):
    def test_dfs(self):
        ctx = Context(dict(zip(impl.FUNCTIONS, np.ones(len(impl.FUNCTIONS)))))

        inputs_list = [
            [ListValue([1,2,3,4,5])],
        ]
        output_list = [
            ListValue([2,4,6,8,10]),
        ]
        examples = list(zip(inputs_list, output_list))


        T = 2
        solution, nb_steps = dfs(examples, T, ctx)
        for inputs, output in examples:
            self.assertEqual(solution(*inputs), output)
        self.assertTrue(nb_steps > 10)

    def test_dfs1(self):
        ctx = Context(dict(zip(impl.FUNCTIONS, np.ones(len(impl.FUNCTIONS)))))

        inputs_list = [
            [ListValue([1,-2,3,-4,5,-6,7])],
        ]
        output_list = [
            ListValue([1,3,15,105])
        ]
        examples = list(zip(inputs_list, output_list))

        T = 3
        solution, nb_steps = dfs(examples, T, ctx)
        for inputs, output in examples:
            self.assertEqual(solution(*inputs), output)
        self.assertTrue(nb_steps > 10)


    def test_impossible(self):
        """Return the first n primes which is impossible in this language."""
        ctx = Context(dict(zip(impl.FUNCTIONS, np.ones(len(impl.FUNCTIONS)))))

        inputs_list = [
            [ListValue(list(range(6)))],
        ]
        output_list = [ListValue([2,3,5,7,11,13])]

        examples = list(zip(inputs_list, output_list))

        T = 2
        solution, nb_steps = dfs(examples, T, ctx)
        self.assertFalse(solution)
        self.assertTrue(nb_steps > 2000)


    def test_enumerate(self):
        used = [impl.MAP, impl.FILTER, impl.COUNT] + [impl.GT0, impl.LT0, impl.EVEN, impl.ODD]
        weights = np.ones(len(used))
        ctx = Context(dict(zip(used, weights)))

        input_type_combinations = [
            [LIST]
        ]
        T = 1
        programs = enumerate_programs(input_type_combinations, T, ctx, 1000)
        self.assertEqual(len(programs), 8)

if __name__ == '__main__':
    unittest.main()
