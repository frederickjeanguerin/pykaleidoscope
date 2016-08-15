from lexer import *
from ast import *
from collections import namedtuple

@unique
class Associativity(Enum):
    UNDEFINED = 0
    LEFT = 1
    RIGHT = 2 

BinOpInfo = namedtuple('BinOpInfo', ['precedence', 'associativity'])

BUILTIN_OP = {
    '=': BinOpInfo(2, Associativity.RIGHT),
    '<': BinOpInfo(10, Associativity.LEFT), 
    '+': BinOpInfo(20, Associativity.LEFT), 
    '-': BinOpInfo(20, Associativity.LEFT), 
    '*': BinOpInfo(40, Associativity.LEFT)}

FALSE_BINOP_INFO = BinOpInfo(-1, Associativity.UNDEFINED)

def builtin_operators():
    return sorted(BUILTIN_OP.keys())  

_binop_map = dict(BUILTIN_OP)

def binop_info(tok):
    kind, value = tok
    try:
        return _binop_map[value] 
    except KeyError:
        if kind == TokenKind.OPERATOR and value not in Parser.PUNCTUATORS:
            raise ParseError("Undefined operator: " + value)
        # Return a false binop info that has no precedence    
        return FALSE_BINOP_INFO

def set_binop_info(op, precedence, associativity):
    _binop_map[op] = BinOpInfo(precedence, associativity)


class ParseError(Exception): pass

class Parser(object):
    """Parser for the Kaleidoscope language.
    After the parser is created, invoke parse_toplevel multiple times to parse
    Kaleidoscope source into an AST.
    """
    def __init__(self):
        self.token_generator = None
        self.cur_tok = None

    # toplevel ::= definition | external | expression
    def parse_toplevel(self, buf):
        return next(self.parse_generator(buf))

    def parse_generator(self, buf):
        """Given a string, returns an AST node representing it."""
        self.token_generator = Lexer(buf).tokens()
        self.cur_tok = None
        self._get_next_token()

        while self.cur_tok.kind != TokenKind.EOF:
            if self.cur_tok.kind == TokenKind.EXTERN:
                yield self._parse_external()
            elif self.cur_tok.kind == TokenKind.DEF:
                yield self._parse_definition()
            else:
                yield self._parse_toplevel_expression()

    def _get_next_token(self):
        self.cur_tok = next(self.token_generator)

    def _match(self, expected_kind, expected_value=None):
        """Consume the current token; verify that it's of the expected kind.
        If expected_kind == TokenKind.OPERATOR, verify the operator's value.
        """
        if (expected_kind == TokenKind.OPERATOR and
            not self._cur_tok_is_operator(expected_value)):
            raise ParseError('Expected "{0}" but got "{1}"'.format(expected_value, self.cur_tok.value))
        elif expected_kind != self.cur_tok.kind:
            raise ParseError('Expected "{0}"'.format(expected_kind))
        self._get_next_token()  


    def _cur_tok_is_operator(self, op):
        """Query whether the current token is the operator op"""
        return (self.cur_tok.kind == TokenKind.OPERATOR and
                self.cur_tok.value == op)

    # identifierexpr
    #   ::= identifier
    #   ::= identifier '(' expression* ')'
    def _parse_identifier_expr(self):
        id_name = self.cur_tok.value
        self._get_next_token()
        # If followed by a '(' it's a call; otherwise, a simple variable ref.
        if not self._cur_tok_is_operator('('):
            return Variable(id_name)

        self._get_next_token()
        args = []
        if not self._cur_tok_is_operator(')'):
            while True:
                args.append(self._parse_expression())
                if self._cur_tok_is_operator(')'):
                    break
                self._match(TokenKind.OPERATOR, ',')

        self._get_next_token()  # consume the ')'
        return Call(id_name, args)

    # numberexpr ::= number
    def _parse_number_expr(self):
        result = Number(self.cur_tok.value)
        self._get_next_token()  # consume the number
        return result

    # parenexpr ::= '(' expression ')'
    def _parse_paren_expr(self):
        self._get_next_token()  # consume the '('
        expr = self._parse_expression()
        self._match(TokenKind.OPERATOR, ')')
        return expr

    # primary
    #   ::= identifierexpr
    #   ::= numberexpr
    #   ::= parenexpr
    #   ::= ifexpr
    #   ::= forexpr
    #   ::= unaryexpr

    PUNCTUATORS = '()[]{};,:'

    def _parse_primary(self):
        if self.cur_tok.kind == TokenKind.IDENTIFIER:
            return self._parse_identifier_expr()
        elif self.cur_tok.kind == TokenKind.NUMBER:
            return self._parse_number_expr()
        elif self._cur_tok_is_operator('('):
            return self._parse_paren_expr()
        elif self.cur_tok.kind == TokenKind.IF:
            return self._parse_if_expr()
        elif self.cur_tok.kind == TokenKind.FOR:
            return self._parse_for_expr()
        elif self.cur_tok.kind == TokenKind.VAR:
            return self._parse_var_expr()            
        elif self.cur_tok.kind == TokenKind.OPERATOR:
            if self.cur_tok.value in Parser.PUNCTUATORS :
                raise ParseError('Expression expected but met with: ' + self.cur_tok.value)
            return self._parse_unaryop_expr()
        elif self.cur_tok.kind == TokenKind.EOF:
            raise ParseError('Expression expected but reached end of code')            
        else:
            raise ParseError('Expression expected but met unknown token', self.cur_tok)

    # ifexpr ::= 'if' expression 'then' expression 'else' expression
    def _parse_if_expr(self):
        self._get_next_token()  # consume the 'if'
        cond_expr = self._parse_expression()
        self._match(TokenKind.THEN)
        then_expr = self._parse_expression()
        self._match(TokenKind.ELSE)
        else_expr = self._parse_expression()
        return If(cond_expr, then_expr, else_expr)

    # forexpr ::= 'for' identifier '=' expr ',' expr (',' expr)? 'in' expr
    def _parse_for_expr(self):
        self._get_next_token()  # consume the 'for'
        id_name = self.cur_tok.value
        self._match(TokenKind.IDENTIFIER)
        self._match(TokenKind.OPERATOR, '=')
        start_expr = self._parse_expression()
        self._match(TokenKind.OPERATOR, ',')
        end_expr = self._parse_expression()

        # The step part is optional
        if self._cur_tok_is_operator(','):
            self._get_next_token()
            step_expr = self._parse_expression()
        else:
            step_expr = None
        self._match(TokenKind.IN)
        body = self._parse_expression()
        return For(id_name, start_expr, end_expr, step_expr, body)

    # varexpr ::= 'var' ( identifier ('=' expr)? )+ 'in' expr
    def _parse_var_expr(self):
        self._get_next_token()  # consume the 'var'
        vars = []

        # At least one variable name is required
        if self.cur_tok.kind != TokenKind.IDENTIFIER:
            raise ParseError('expected identifier after "var"')

        while self.cur_tok.kind != TokenKind.IN:
            name = self.cur_tok.value
            self._get_next_token()  # consume the identifier

            # Parse the optional initializer
            if self._cur_tok_is_operator('='):
                self._get_next_token()  # consume the '='
                init = self._parse_expression()
            else:
                init = None
            vars.append((name, init))

        self._match(TokenKind.IN)
        body = self._parse_expression()
        return VarIn(vars, body)

    # binoprhs ::= (<binop> primary)*
    def _parse_binop_rhs(self, expr_prec, lhs):
        """Parse the right-hand-side of a binary expression.
        expr_prec: minimal precedence to keep going (precedence climbing).
        lhs: AST of the left-hand-side.
        """
        while True:
            cur_prec, cur_assoc = binop_info(self.cur_tok)
            # If this is a binary operator with precedence lower than the
            # currently parsed sub-expression, bail out. If it binds at least
            # as tightly, keep going.
            # Note that the precedence of non-operators is defined to be -1,
            # so this condition handles cases when the expression ended.
            if cur_prec < expr_prec:
                return lhs
            op = self.cur_tok.value
            self._get_next_token()  # consume the operator
            rhs = self._parse_primary()

            next_prec, next_assoc = binop_info(self.cur_tok)
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
                rhs = self._parse_binop_rhs(cur_prec + 1, rhs)

            if cur_prec == next_prec and next_assoc == Associativity.RIGHT:
                rhs = self._parse_binop_rhs(cur_prec, rhs)

            # Merge lhs/rhs
            lhs = Binary(op, lhs, rhs)

    # expression ::= primary binoprhs
    def _parse_expression(self):
        lhs = self._parse_primary()
        # Start with precedence 0 because we want to bind any operator to the
        # expression at this point.
        return self._parse_binop_rhs(0, lhs)

    # unary ::= op primary    
    def _parse_unaryop_expr(self):   
        op = self.cur_tok.value
        self._get_next_token()
        rhs = self._parse_primary()
        return Unary(op, rhs) 

    # prototype
    #   ::= id '(' id* ')'
    #   ::= 'binary' LETTER number? '(' id id ')'
    #   ::= 'unary' LETTER '(' id id ')'    
    def _parse_prototype(self):
        prec = DEFAULT_PREC 
        if self.cur_tok.kind == TokenKind.IDENTIFIER:
            name = self.cur_tok.value
            self._get_next_token()
        elif self.cur_tok.kind == TokenKind.UNARY:
            self._get_next_token()
            if self.cur_tok.kind != TokenKind.OPERATOR:
                raise ParseError('Expected operator after "unary"')
            name = 'unary{0}'.format(self.cur_tok.value)
            self._get_next_token()
        elif self.cur_tok.kind == TokenKind.BINARY:
            self._get_next_token()
            if self.cur_tok.kind != TokenKind.OPERATOR:
                raise ParseError('Expected operator after "binary"')
            name = 'binary{0}'.format(self.cur_tok.value)
            self._get_next_token()

            # Try to parse precedence
            if self.cur_tok.kind == TokenKind.NUMBER:
                prec = int(self.cur_tok.value)
                if not (0 < prec < 101):
                    raise ParseError('Invalid precedence', prec)
                self._get_next_token()

            # Add the new operator to our precedence table so we can properly
            # parse it.
            set_binop_info(name[-1], prec, Associativity.LEFT)

        self._match(TokenKind.OPERATOR, '(')
        argnames = []
        while self.cur_tok.kind == TokenKind.IDENTIFIER:
            argnames.append(self.cur_tok.value)
            self._get_next_token()
        self._match(TokenKind.OPERATOR, ')')

        if name.startswith('binary') and len(argnames) != 2:
            raise ParseError('Expected binary operator to have 2 operands')
        elif name.startswith('unary') and len(argnames) != 1:
            raise ParseError('Expected unary operator to have one operand')

        return Prototype(
            name, argnames, name.startswith(('unary', 'binary')), prec)

    # external ::= 'extern' prototype
    def _parse_external(self):
        self._get_next_token()  # consume 'extern'
        return self._parse_prototype()

    # definition ::= 'def' prototype expression
    def _parse_definition(self):
        self._get_next_token()  # consume 'def'
        proto = self._parse_prototype()
        expr = self._parse_expression()
        return Function(proto, expr)

    # toplevel ::= expression
    def _parse_toplevel_expression(self):
        expr = self._parse_expression()
        # Anonymous function
        return Function.Anonymous(expr)

#---- Some unit tests ----#


class TestParser(unittest.TestCase):

    def _assert_body(self, toplevel, expected):
        """Assert the flattened body of the given toplevel function"""
        self.assertIsInstance(toplevel, Function)
        self.assertEqual(toplevel.body.flatten(), expected)

    def test_basic(self):
        ast = Parser().parse_toplevel('2')
        self.assertIsInstance(ast, Function)
        self.assertIsInstance(ast.body, Number)
        self.assertEqual(ast.body.val, '2')

    def test_basic_with_flattening(self):
        ast = Parser().parse_toplevel('2')
        self._assert_body(ast, ['Number', '2'])

        ast = Parser().parse_toplevel('foobar')
        self._assert_body(ast, ['Variable', 'foobar'])

    def test_expr_singleprec(self):
        ast = Parser().parse_toplevel('2+ 3-4')
        self._assert_body(ast,
            ['Binary',
                '-', ['Binary', '+', ['Number', '2'], ['Number', '3']],
                ['Number', '4']])

    def test_expr_multiprec(self):
        ast = Parser().parse_toplevel('2+3*4-9')
        self._assert_body(ast,
            ['Binary', '-',
                ['Binary', '+',
                    ['Number', '2'],
                    ['Binary', '*', ['Number', '3'], ['Number', '4']]],
                ['Number', '9']])

    def test_expr_parens(self):
        ast = Parser().parse_toplevel('2*(3-4)*7')
        self._assert_body(ast,
            ['Binary', '*',
                ['Binary', '*',
                    ['Number', '2'],
                    ['Binary', '-', ['Number', '3'], ['Number', '4']]],
                ['Number', '7']])

    def test_externals(self):
        ast = Parser().parse_toplevel('extern sin(arg)')
        self.assertEqual(ast.flatten(), ['Prototype', 'sin', '(arg)'])

        ast = Parser().parse_toplevel('extern Foobar(nom denom abom)')
        self.assertEqual(ast.flatten(),
            ['Prototype', 'Foobar', '(nom denom abom)'])

    def test_funcdef(self):
        ast = Parser().parse_toplevel('def foo(x) 1 + bar(x)')
        self.assertEqual(ast.flatten(),
            ['Function', ['Prototype', 'foo', '(x)'],
                ['Binary', '+',
                    ['Number', '1'],
                    ['Call', 'bar', [['Variable', 'x']]]]])

    def test_unary(self):
        p = Parser()
        ast = p.parse_toplevel('def unary!(x) 0 - x')
        self.assertIsInstance(ast, Function)
        proto = ast.proto
        self.assertIsInstance(proto, Prototype)
        self.assertTrue(proto.isoperator)
        self.assertEqual(proto.name, 'unary!')

        ast = p.parse_toplevel('!a + !b - !!c')
        self._assert_body(ast,
            ['Binary', '-',
                ['Binary', '+',
                    ['Unary', '!', ['Variable', 'a']],
                    ['Unary', '!', ['Variable', 'b']]],
                ['Unary', '!', ['Unary', '!', ['Variable', 'c']]]])

    def test_binary_op_no_prec(self):
        ast = Parser().parse_toplevel('def binary $(a b) a + b')
        self.assertIsInstance(ast, Function)
        proto = ast.proto
        self.assertIsInstance(proto, Prototype)
        self.assertTrue(proto.isoperator)
        self.assertEqual(proto.prec, DEFAULT_PREC)
        self.assertEqual(proto.name, 'binary$')

    def test_binary_op_with_prec(self):
        ast = Parser().parse_toplevel('def binary% 77(a b) a + b')
        self.assertIsInstance(ast, Function)
        proto = ast.proto
        self.assertIsInstance(proto, Prototype)
        self.assertTrue(proto.isoperator)
        self.assertEqual(proto.prec, 77)
        self.assertEqual(proto.name, 'binary%')

    def test_binop_relative_precedence(self):
        # with precedence 77, % binds stronger than all existing ops
        p = Parser()
        p.parse_toplevel('def binary% 77(a b) a + b')
        ast = p.parse_toplevel('a * 10 % 5 * 10')
        self._assert_body(ast,
            ['Binary', '*',
                ['Binary', '*',
                    ['Variable', 'a'],
                    ['Binary', '%', ['Number', '10'], ['Number', '5']]],
                ['Number', '10']])

        ast = p.parse_toplevel('a % 20 * 5')
        self._assert_body(ast,
            ['Binary', '*',
                ['Binary', '%', ['Variable', 'a'], ['Number', '20']],
                ['Number', '5']])

    def test_binop_right_associativity(self):
        p = Parser()
        ast = p.parse_toplevel('x = y = 10 + 5')
        self._assert_body(ast,
            ['Binary', '=',
                ['Variable', 'x'],
                ['Binary', '=',
                    ['Variable', 'y'],
                    ['Binary', '+', ['Number', '10'], ['Number', '5']]]])

#---- Typical example use ----#

if __name__ == '__main__':

    import run
    run.repl(parseonly = True) 
