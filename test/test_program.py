import unittest

import numpy as np

from deepcoder.dsl.program import Program, prune, get_unused_indices
from deepcoder.dsl.value import IntValue, ListValue

class TestProgram(unittest.TestCase):
    def test_basic(self):
        # takes the second highest negative number
        prefix = 'LIST|INT|FILTER,<0,0|SORT,2|REVERSE,3|ACCESS,1,4'
        program = Program.parse(prefix)

        expected = IntValue(-2)
        actual = program(ListValue([1, -5, -3, -4, -2, -1, 2, 3]), IntValue(1))

        self.assertEqual(actual, expected)
        self.assertEqual(program.toprefix(), prefix)


    def test_prune(self):
        prefix = 'LIST|INT|MAP,*2,0|FILTER,>0,0|FILTER,<0,2'
        p = Program.parse(prefix)
        pp = prune(p)
        expected = 'LIST|MAP,*2,0|FILTER,<0,1'
        self.assertEqual(pp.toprefix(), expected)


    def test_get_unused_indices(self):
        prefix = 'LIST|INT|MAP,*2,0|FILTER,>0,0|FILTER,<0,2'
        program = Program.parse(prefix)
        expected = {1, 3}
        actual = get_unused_indices(program)
        self.assertEqual(actual, expected)



if __name__ == '__main__':
    unittest.main()
