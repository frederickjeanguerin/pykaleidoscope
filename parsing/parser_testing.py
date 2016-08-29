
import unittest
from .parser import *

def parse_toplevel(buf):
    return next(ast_from(Source("parsing tests", buf)))

class TestParser(unittest.TestCase):

    def _assert_ast(f, ast, expected_flattened_ast):
        f.assertEqual(ast.flatten(), expected_flattened_ast)

    def _assert_parse(f, codestr, expected_flattened_ast):
        f.assertEqual(
            parse_toplevel(codestr).flatten(), 
            expected_flattened_ast)

    def _assert_body(f, toplevel, expected):
        """Assert the flattened body of the given toplevel function"""
        f.assertIsInstance(toplevel, Function)
        f.assertEqual(toplevel.body.flatten(), expected)

    def test_basic(f):
        ast = parse_toplevel('2')
        f.assertIsInstance(ast, Number)
        f.assertEqual(ast.val, '2')

    def test_basic_with_flattening(f):
        f._assert_parse('2', ['Number', '2'])
        f._assert_parse('foobar', ['Variable', 'foobar'])

    def test_expr_singleprec(f):
        f._assert_parse('2+ 3-4',
            ['Binary',
                '-', ['Binary', '+', ['Number', '2'], ['Number', '3']],
                ['Number', '4']])

    def test_expr_multiprec(f):
        f._assert_parse('2+3*4-9',
            ['Binary', '-',
                ['Binary', '+',
                    ['Number', '2'],
                    ['Binary', '*', ['Number', '3'], ['Number', '4']]],
                ['Number', '9']])

    def test_expr_parens(f):
        f._assert_parse('2*(3-4)*7',
            ['Binary', '*',
                ['Binary', '*',
                    ['Number', '2'],
                    ['Binary', '-', ['Number', '3'], ['Number', '4']]],
                ['Number', '7']])

    def test_externals(f):
        f._assert_parse('extern sin(arg)', ['Prototype', 'sin', ['arg']])

        f._assert_parse('extern Foobar(nom denom abom)',
            ['Prototype', 'Foobar', ['nom', 'denom', 'abom']])

    def test_funcdef(f):
        f._assert_parse('def foo(x) 1 + bar(x)',
            ['Function', ['Prototype', 'foo', ['x']],
                ['Binary', '+',
                    ['Number', '1'],
                    ['Call', 'bar', [['Variable', 'x']]]]])

    def test_unary(f):
        ast = parse_toplevel('def unary!(x) 0 - x')
        f.assertIsInstance(ast, Function)
        proto = ast.proto
        f.assertIsInstance(proto, Prototype)
        f.assertEqual(proto.name, 'unary!')

        ast = parse_toplevel('!a + !b - !!c')
        f._assert_ast(ast,
            ['Binary', '-',
                ['Binary', '+',
                    ['Unary', '!', ['Variable', 'a']],
                    ['Unary', '!', ['Variable', 'b']]],
                ['Unary', '!', ['Unary', '!', ['Variable', 'c']]]])

    def test_binary_op(f):
        ast = parse_toplevel('def binary$ (a b) a + b')
        f.assertIsInstance(ast, Function)
        proto = ast.proto
        f.assertIsInstance(proto, Prototype)
        f.assertEqual(proto.name, 'binary$')


    def test_binop_right_associativity(f):
        f._assert_parse('x = y = 10 + 5',
            ['Binary', '=',
                ['Variable', 'x'],
                ['Binary', '=',
                    ['Variable', 'y'],
                    ['Binary', '+', ['Number', '10'], ['Number', '5']]]])

    def test_var(f):
        f._assert_parse('var x in x',
            ['VarIn', 
                [('x', None)],
                ['Variable', 'x']])

        f._assert_parse('var x y = 10 in x',
            ['VarIn', 
                [('x', None), ('y', Number("10"))],
                ['Variable', 'x']])