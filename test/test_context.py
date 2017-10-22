import unittest

from deepcoder.context import Context
from deepcoder.dsl import impl

class TestContext(unittest.TestCase):
    def test_context(self):

        scores_map = {
            impl.MAP: 1.,
            impl.FILTER: .5,
            impl.COUNT: .5,
            impl.TIMES2: 1.,
            impl.MINUS1: 0.
        }

        ctx = Context(scores_map)

        self.assertEqual(set(ctx.functions), {impl.MAP, impl.FILTER, impl.COUNT})
        func_scores = [scores_map[x] for x in ctx.functions]
        self.assertEqual(func_scores, list(reversed(sorted(func_scores))))

        for _, funcs in ctx.typemap.items():
            func_scores = [scores_map[x] for x in funcs]
            self.assertEqual(func_scores, list(reversed(sorted(func_scores))))

        self.assertEqual(len(ctx.typemap), 4)

if __name__ == '__main__':
    unittest.main()
