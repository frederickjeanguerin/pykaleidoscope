
from lexing.lexer import TokenKind
import binop
from token_feeder import TokenFeeder
from ast import *

PUNCTUATORS = '()[]{};,:'

# toplevel ::= definition | external | expression
def ast_from(source):
    """Given a string, returns an AST node representing it."""

    f = TokenFeeder(source)

    while not f.match(TokenKind.EOF):
        if f.match(TokenKind.EXTERN):
            yield _parse_external(f)
        elif f.match(TokenKind.DEF):
            yield _parse_definition(f)
        else:
            yield _parse_expr(f)


def binop_info(tok):
    """ Return a BinOpInfo about the current token.
        If not an operator, return a precedence of -1 
        and undefined associativy.
        Raise an error if the operator is not defined.
    """
    info = binop.info(tok.text)
    if info:
        return info
    else:    
        if tok.kind == TokenKind.OPERATOR and tok.text not in PUNCTUATORS:
            f.throw("Undefined operator")
        # Return a false binop info that has no precedence    
        return binop.BinOpInfo(-1, binop.Associativity.UNDEFINED)
    

# identifierexpr
#   ::= identifier
#   ::= identifier '(' expression* ')'
def _parse_identifier_expr(f):
    id_name = f.current.text
    f.eat(TokenKind.IDENTIFIER)

    # If followed by a '(' it's a call; otherwise, a simple variable ref.
    if not f.match('('):
        return Variable(id_name)

    # Ok, it's a call    
    f.eat('(')
    args = []
    if not f.match(')'):
        while True:
            args.append(_parse_expr(f))
            if f.match(')'):
                break
            f.eat(',')

    f.eat(')')  
    return Call(id_name, args)

# numberexpr ::= number
def _parse_number_expr(f):
    result = Number(f.current.text)
    f.eat(TokenKind.NUMBER)
    return result

# parenexpr ::= '(' expression ')'
def _parse_paren_expr(f):
    f.eat('(') 
    expr = _parse_expr(f)
    f.eat(')')
    return expr

# primary
#   ::= identifierexpr
#   ::= numberexpr
#   ::= parenexpr
#   ::= ifexpr
#   ::= forexpr
#   ::= unaryexpr

def _parse_primary(f):
    if f.match(TokenKind.IDENTIFIER):
        return _parse_identifier_expr(f)
    elif f.match(TokenKind.NUMBER):
        return _parse_number_expr(f)
    elif f.match('('):
        return _parse_paren_expr(f)
    elif f.match(TokenKind.IF):
        return _parse_if_expr(f)
    elif f.match(TokenKind.FOR):
        return _parse_for_expr(f)
    elif f.match(TokenKind.VAR):
        return _parse_var_expr(f)            
    elif f.match(TokenKind.OPERATOR):
        if f.current.text in PUNCTUATORS :
            f.throw('Expression expected before punctuator')
        return _parse_unaryop_expr(f)
    elif f.match(TokenKind.EOF):
        f.throw('Expression expected before end of code')            
    else:
        f.throw('Expression expected but met unknown token')

# ifexpr ::= 'if' expression 'then' expression 'else' expression
def _parse_if_expr(f):
    f.eat(TokenKind.IF)  
    cond_expr = _parse_expr(f)
    f.eat(TokenKind.THEN)
    then_expr = _parse_expr(f)
    f.eat(TokenKind.ELSE)
    else_expr = _parse_expr(f)
    return If(cond_expr, then_expr, else_expr)

# forexpr ::= 'for' identifier '=' expr ',' expr (',' expr)? 'in' expr
def _parse_for_expr(f):
    f.eat(TokenKind.FOR)  
    id_name = f.current.text
    f.eat(TokenKind.IDENTIFIER)
    f.eat('=')
    start_expr = _parse_expr(f)
    f.eat(',')
    end_expr = _parse_expr(f)

    # The step part is optional
    if f.match_then_eat(','):
        step_expr = _parse_expr(f)
    else:
        step_expr = None
    f.eat(TokenKind.IN)
    body = _parse_expr(f)
    return For(id_name, start_expr, end_expr, step_expr, body)

# varexpr ::= 'var' ( identifier ('=' expr)? )+ 'in' expr
def _parse_var_expr(f):
    f.eat(TokenKind.VAR) 
    vars = []

    # At least one variable name is required
    f.expect(TokenKind.IDENTIFIER)

    while not f.match(TokenKind.IN):
        name = f.current.text
        f.eat(TokenKind.IDENTIFIER)  

        # Parse the optional initializer
        if f.match_then_eat('='):
            init = _parse_expr(f)
        else:
            init = None
        vars.append((name, init))

        # Parse the optional comma
        f.match_then_eat(',')
    f.eat(TokenKind.IN)
    body = _parse_expr(f)
    return VarIn(vars, body)

# binoprhs ::= (<binop> primary)*
def _parse_binop_rhs(f, expr_prec, lhs):
    """Parse the right-hand-side of a binary expression.
    expr_prec: minimal precedence to keep going (precedence climbing).
    lhs: AST of the left-hand-side.
    """
    while True:
        cur_prec, cur_assoc = binop_info(f.current)
        # If this is a binary operator with precedence lower than the
        # currently parsed sub-expression, bail out. If it binds at least
        # as tightly, keep going.
        # Note that the precedence of non-operators is defined to be -1,
        # so this condition handles cases when the expression ended.
        if cur_prec < expr_prec:
            return lhs
        op = f.current.text
        f.eat(TokenKind.OPERATOR) 
        rhs = _parse_primary(f)

        next_prec, next_assoc = binop_info(f.current)
        # There are four options:
        # 1. next_prec > cur_prec: we need to make a recursive call
        # 2. next_prec == cur_prec and operator is left-associative: 
        #    no need for a recursive call, the next
        #    iteration of this loop will handle it.
        # 3. next_prec == cur_prec and operator is right-associative:
        #    make a recursive call 
        # 4. next_prec < cur_prec: no need for a recursive call, combine
        #    lhs and the next iteration will immediately bail out.
        if cur_prec < next_prec:
            rhs = _parse_binop_rhs(f, cur_prec + 1, rhs)

        if cur_prec == next_prec and next_assoc == binop.Associativity.RIGHT:
            rhs = _parse_binop_rhs(f, cur_prec, rhs)

        # Merge lhs/rhs
        lhs = Binary(op, lhs, rhs)

# expression ::= primary binoprhs
def _parse_expr(f):
    lhs = _parse_primary(f)
    # Start with precedence 0 because we want to bind any operator to the
    # expression at this point.
    return _parse_binop_rhs(f, 0, lhs)

# unary ::= op primary    
def _parse_unaryop_expr(f):   
    op = f.current.text
    f.eat(TokenKind.OPERATOR)
    rhs = _parse_primary(f)
    return Unary(op, rhs) 

# prototype
#   ::= id '(' id* ')'
def _parse_prototype(f):
    idtok = f.eat(TokenKind.IDENTIFIER)

    f.eat('(')
    argnames = []
    while f.match(TokenKind.IDENTIFIER):
        argnames.append(f.eat().text)
    f.eat(')')

    if idtok.subkind == TokenKind.BINARY and len(argnames) != 2:
        f._raise('Binary operator should have 2 operands', idtok)
    elif idtok.subkind == TokenKind.UNARY and len(argnames) != 1:
        f._raise('Unary operator should have just one operand', idtok)

    return Prototype(idtok.text, argnames)

# external ::= 'extern' prototype
def _parse_external(f):
    f.eat(TokenKind.EXTERN) 
    return _parse_prototype(f)

# definition ::= 'def' prototype expression
def _parse_definition(f):
    f.eat(TokenKind.DEF) 
    proto = _parse_prototype(f)
    expr = _parse_expr(f)
    return Function(proto, expr)

#---- Some unit tests ----#

import unittest
from lexing.source import Source

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


#---- Typical example use ----#

if __name__ == '__main__':

    import sys
    if sys.argv[1:] == ['--repl']:
        import kal
        kal.run(parseonly = True)
    else:
        unittest.main()
     
