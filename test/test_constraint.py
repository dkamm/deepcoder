import unittest

import numpy as np

from deepcoder.dsl import constants
from deepcoder.dsl import constraint
from deepcoder.dsl import impl
from deepcoder.dsl.program import Program
from deepcoder.dsl.types import LIST

class TestConstraint(unittest.TestCase):
    def test_sample(self):
        ic = constraint.IntConstraint(-5, 5)
        val = constraint.sample(ic)
        self.assertTrue(val <= 5)
        self.assertTrue(val >= -5)

        lc = constraint.ListConstraint(1, 4, [ic] * 4)
        val = constraint.sample(lc)
        self.assertTrue(len(val) <= 4)
        self.assertTrue(len(val) >= 1)

        for x in val:
            self.assertTrue(x <= 5)
            self.assertTrue(x >= -5)

        lc = constraint.ListConstraint(0, 0, [ic] * 4)
        val = constraint.sample(lc)
        self.assertEqual(val, [])


        with self.assertRaises(constraint.InvalidConstraintError) as context:
            ic = constraint.IntConstraint(1,0)
            constraint.sample(ic)
            self.assertTrue('invalid constraint {}'.format(ic) in context.exception)
        with self.assertRaises(constraint.InvalidConstraintError) as context:
            ic = constraint.IntConstraint(1,0)
            lc = constraint.ListConstraint(1, 4, [ic] * 4)
            constraint.sample(lc)
            self.assertTrue('invalid constraint {}'.format(lc) in context.exception)

    def test_map_constraints(self):
        expectedmap = {
            impl.PLUS1: constraint.IntConstraint(-11, 3),
            impl.MINUS1: constraint.IntConstraint(-9, 5),
            impl.TIMES2: constraint.IntConstraint(-5, 2),
            impl.TIMES3: constraint.IntConstraint(-3, 1),
            impl.TIMES4: constraint.IntConstraint(-2, 1),
            impl.TIMESNEG1: constraint.IntConstraint(-4, 10),
            impl.POW2: constraint.IntConstraint(-2, 2)
        }

        ic = constraint.IntConstraint(-10, 4)
        for lmbda, expected in expectedmap.items():
            ics = [ic] * 4
            lc = constraint.ListConstraint(1, 4, ics)
            stmt = impl.MAP, (lmbda, 0)

            lc1 = constraint.get_constraints_from_stmt(stmt, lc)[0]

            self.assertEqual(lc.lmin, lc1.lmin)
            self.assertEqual(lc.lmax, lc1.lmax)
            for ic1 in lc1.int_constraints:
                self.assertEqual(ic1, expected)

    def test_clip(self):
        expectedmap = {
            impl.PLUS1: constraint.IntConstraint(-256, 255),
        }

        ic = constraint.IntConstraint()
        for lmbda, expected in expectedmap.items():
            ics = [ic] * 4
            lc = constraint.ListConstraint(1, 4, ics)
            stmt = impl.MAP, (lmbda, 0)

            lc1 = constraint.get_constraints_from_stmt(stmt, lc)[0]

            self.assertEqual(lc.lmin, lc1.lmin)
            self.assertEqual(lc.lmax, lc1.lmax)
            for ic1 in lc1.int_constraints:
                self.assertEqual(ic1, expected)


    def test_zipwith_constraints(self):
        expectedmap = {
            impl.LPLUS : constraint.IntConstraint(-5, 2),
            impl.LMINUS : constraint.IntConstraint(-5, 2),
            impl.LTIMES : constraint.IntConstraint(-2, 2),
        }

        ic = constraint.IntConstraint(-10, 4)
        for lmbda, expected in expectedmap.items():
            ics = [ic] * 4
            expected_lc = constraint.ListConstraint(1, 4, ics)
            stmt = impl.ZIPWITH, (lmbda, 0, 1)

            actual_lcs = constraint.get_constraints_from_stmt(stmt, expected_lc)

            for actual_lc in actual_lcs:
                self.assertEqual(expected_lc.lmin, actual_lc.lmin)
                self.assertEqual(expected_lc.lmax, actual_lc.lmax)
                for actual_ic in actual_lc.int_constraints:
                    self.assertEqual(actual_ic, expected)

    def test_scan1l_constraints(self):
        INTMIN = constraint.INTMIN
        INTMAX = constraint.INTMAX
        expectedmap = {
            impl.LPLUS: constraint.ListConstraint(1, 4,
                [constraint.IntConstraint()] +
                [constraint.IntConstraint(int(INTMIN / l), int(INTMAX / l))
                 for l in range(1, 5)]),
            impl.LMINUS: constraint.ListConstraint(1, 4,
                [constraint.IntConstraint()] +
                [constraint.IntConstraint(int(INTMIN / l), int(INTMAX / l))
                 for l in range(1, 5)]),
            impl.LTIMES: constraint.ListConstraint(1, 4,
                [constraint.IntConstraint()] +
                [constraint.IntConstraint(-int(10 ** (np.log10(INTMAX) / l)), int(10 ** (np.log10(INTMAX) / l)))
                 for l in range(1, 5)]),
        }

        output_lc = constraint.ListConstraint(1, 4)
        for lmbda, expected in expectedmap.items():
            stmt = impl.SCAN1L, (lmbda, 0)
            actual = constraint.get_constraints_from_stmt(stmt, output_lc)[0]
            self.assertEqual(expected, actual)

    def test_propagate(self):
        stmts = [
            (impl.MAP, (impl.TIMES2, 0)),
            (impl.FILTER, (impl.GT0, 1)),
            (impl.MAP, (impl.MINUS1, 2)),
        ]

        p = Program([LIST], stmts)

        output_constraint = constraint.ListConstraint(1, 4,
            [constraint.IntConstraint(-5, 3)] * 5)
        actual = constraint.propagate_constraints(p, output_constraint)[0]
        expected = constraint.ListConstraint(1, 4,
            [constraint.IntConstraint(-2, 2)] * 5)

        self.assertEqual(expected, actual)

    def test_is_same(self):

        lhs = Program.parse('LIST|MAXIMUM,0')
        rhs = Program.parse('LIST|SCAN1L,max,0|MAXIMUM,1')

        self.assertTrue(constraint.is_same(lhs, rhs))

    def test_null_allowed(self):
        p = Program.parse('LIST|TAIL,0|ACCESS,1,0')
        expected = [
            constraint.ListConstraint(
                lmin=1,
                int_constraints=[constraint.IntConstraint(0, l-1) for l in range(constraint.L+1)] 
            ),
            constraint.IntConstraint(0, 256),
            constraint.IntConstraint()
        ]
        output_constraint = constraint.IntConstraint()
        actual = constraint.propagate_constraints(p, output_constraint)
        self.assertEqual(expected, actual)

    def test_null_allowed2(self):
        p = Program.parse('LIST|INT|ACCESS,1,0|ACCESS,2,0')
        expected = [
            constraint.ListConstraint(
                lmin=1,
                int_constraints=[constraint.IntConstraint(0, constants.INTMAX) for l in range(constraint.L+1)] 
            ),
            constraint.IntConstraint(0,0),
            constraint.IntConstraint(0,256),
            constraint.IntConstraint()
        ]
        output_constraint = constraint.IntConstraint()
        actual = constraint.propagate_constraints(p, output_constraint)
        self.assertEqual(expected, actual)



if __name__ == '__main__':
    unittest.main()
