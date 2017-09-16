import unittest


from deepcoder.dsl import impl
from deepcoder.dsl.function import Function
from deepcoder.dsl.constants import NULL
from deepcoder.dsl.types import INT, BOOL, LIST, FunctionType

class TestDSL(unittest.TestCase):
    def test_function_type(self):
        ft = FunctionType(INT, INT)
        self.assertEqual(str(ft), 'F(INT, INT)')
        self.assertEqual(ft.input_types, (INT,))

    def test_function(self):
        f = Function('foo', lambda x: x + 1, INT, INT)
        ftype = FunctionType(INT, INT)

        self.assertEqual(f.type, FunctionType(INT, INT))
        self.assertEqual(str(f.type), 'F(INT, INT)')
        self.assertEqual(f(1), 2)
        self.assertEqual(str(f), 'foo')
        self.assertEqual(f.name, 'foo')

    def test_higher_function(self):
        f = Function('map', lambda f, xs: [f(x) for x in xs] , (FunctionType(INT, INT), LIST), LIST)
        bar = Function('3x', lambda x: 3*x, INT, INT)
        self.assertEqual(f(bar, [1,2,3]), [3,6,9])
        self.assertEqual(f.type, FunctionType((FunctionType(INT, INT), LIST), LIST))
        self.assertEqual(str(f.type), 'F((F(INT, INT), LIST), LIST)')

    def test_impl(self):
        self.assertEqual(impl.MAP(impl.TIMES2, [1,2,3]), [2,4,6])
        self.assertEqual(impl.FILTER(impl.EVEN, [1,2,3]), [2])
        self.assertEqual(impl.COUNT(impl.EVEN, [1,3,5,7]), 0)
        self.assertEqual(impl.ZIPWITH(impl.LMINUS, [1,2,3], [2,3,4]), [-1, -1, -1])
        self.assertEqual(impl.SCAN1L(impl.LTIMES, [1,2,3,4]), [1, 1*2, 1*2*3, 1*2*3*4])
        self.assertEqual(impl.MINIMUM([]), NULL)
        self.assertEqual(impl.MAXIMUM([]), NULL)
        self.assertEqual(impl.ACCESS(0, []), NULL)
        self.assertEqual(impl.ACCESS(4, [1,2,3]), NULL)
        self.assertEqual(impl.TAKE(1, []), [])

if __name__ == '__main__':
    unittest.main()

