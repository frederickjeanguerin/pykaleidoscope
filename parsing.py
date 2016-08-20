
from lexing.lexer import tokens_from, Token, TokenKind
import binop
from ast import *

class ParseError(Exception): 
    """ Expecting two arguments: (message, token). """
    pass

class Parser(object):
    """Parser for the Kaleidoscope language.
    Kaleidoscope source into an AST.
    """
    def __init__(self):
        self.token_generator = None
        self.cur_tok = None

    # toplevel ::= definition | external | expression
    def parse_generator(self, source):
        """Given a string, returns an AST node representing it."""
        self.token_generator = tokens_from(source)
        self.cur_tok = None
        self._eat() # Fetch first token into the parser

        while not self._match(TokenKind.EOF):
            if self._match(TokenKind.EXTERN):
                yield self._parse_external()
            elif self._match(TokenKind.DEF):
                yield self._parse_definition()
            else:
                yield self._parse_expression()

    def _eat(self, token_attribute = None):
        """Consume and return the current token; 
        If argument present, verify that it matches the expected attribute. 
        """
        if token_attribute:
            self._expect(token_attribute)
        previous = self.cur_tok    
        self.cur_tok = next(self.token_generator)
        return previous

    def _expect(self, token_attribute):
        """Verify the current token against the given attribute"""
        if not self._match(token_attribute):
            self._raise('Expected ' + str(token_attribute))

    def _match(self, token_attribute):
        """Return true if the current token matches with the given attribute"""
        return token_attribute in [self.cur_tok.kind, self.cur_tok.text, self.cur_tok.subkind]        

    def _match_then_eat(self, token_attribute):
        """Return true if the current token matches with the given attribute, eating that token by the way"""
        if self._match(token_attribute):
            self._eat()
            return True
        return False            

    def _raise(self, message, token = None):
        """Raise a parse error, passing it a message and the current token"""
        raise ParseError(message, token or self.cur_tok)

    def binop_info(self):
        """ Return a BinOpInfo about the current token.
            If not an operator, return a precedence of -1 
            and undefined associativy.
            Raise an error if the operator is not defined.
        """
        tok = self.cur_tok
        info = binop.info(tok.text)
        if info:
            return info
        else:    
            if tok.kind == TokenKind.OPERATOR and tok.text not in Parser.PUNCTUATORS:
                self._raise("Undefined operator")
            # Return a false binop info that has no precedence    
            return binop.BinOpInfo(-1, binop.Associativity.UNDEFINED)
        

    # identifierexpr
    #   ::= identifier
    #   ::= identifier '(' expression* ')'
    def _parse_identifier_expr(self):
        id_name = self.cur_tok.text
        self._eat(TokenKind.IDENTIFIER)

        # If followed by a '(' it's a call; otherwise, a simple variable ref.
        if not self._match('('):
            return Variable(id_name)

        # Ok, it's a call    
        self._eat('(')
        args = []
        if not self._match(')'):
            while True:
                args.append(self._parse_expression())
                if self._match(')'):
                    break
                self._eat(',')

        self._eat(')')  
        return Call(id_name, args)

    # numberexpr ::= number
    def _parse_number_expr(self):
        result = Number(self.cur_tok.text)
        self._eat(TokenKind.NUMBER)
        return result

    # parenexpr ::= '(' expression ')'
    def _parse_paren_expr(self):
        self._eat('(') 
        expr = self._parse_expression()
        self._eat(')')
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
        if self._match(TokenKind.IDENTIFIER):
            return self._parse_identifier_expr()
        elif self._match(TokenKind.NUMBER):
            return self._parse_number_expr()
        elif self._match('('):
            return self._parse_paren_expr()
        elif self._match(TokenKind.IF):
            return self._parse_if_expr()
        elif self._match(TokenKind.FOR):
            return self._parse_for_expr()
        elif self._match(TokenKind.VAR):
            return self._parse_var_expr()            
        elif self._match(TokenKind.OPERATOR):
            if self.cur_tok.text in Parser.PUNCTUATORS :
                self._raise('Expression expected before punctuator')
            return self._parse_unaryop_expr()
        elif self._match(TokenKind.EOF):
            self._raise('Expression expected before end of code at')            
        else:
            self._raise('Expression expected but met unknown token')

    # ifexpr ::= 'if' expression 'then' expression 'else' expression
    def _parse_if_expr(self):
        self._eat(TokenKind.IF)  
        cond_expr = self._parse_expression()
        self._eat(TokenKind.THEN)
        then_expr = self._parse_expression()
        self._eat(TokenKind.ELSE)
        else_expr = self._parse_expression()
        return If(cond_expr, then_expr, else_expr)

    # forexpr ::= 'for' identifier '=' expr ',' expr (',' expr)? 'in' expr
    def _parse_for_expr(self):
        self._eat(TokenKind.FOR)  
        id_name = self.cur_tok.text
        self._eat(TokenKind.IDENTIFIER)
        self._eat('=')
        start_expr = self._parse_expression()
        self._eat(',')
        end_expr = self._parse_expression()

        # The step part is optional
        if self._match_then_eat(','):
            step_expr = self._parse_expression()
        else:
            step_expr = None
        self._eat(TokenKind.IN)
        body = self._parse_expression()
        return For(id_name, start_expr, end_expr, step_expr, body)

    # varexpr ::= 'var' ( identifier ('=' expr)? )+ 'in' expr
    def _parse_var_expr(self):
        self._eat(TokenKind.VAR) 
        vars = []

        # At least one variable name is required
        self._expect(TokenKind.IDENTIFIER)

        while not self._match(TokenKind.IN):
            name = self.cur_tok.text
            self._eat(TokenKind.IDENTIFIER)  

            # Parse the optional initializer
            if self._match_then_eat('='):
                init = self._parse_expression()
            else:
                init = None
            vars.append((name, init))

            # Parse the optional comma
            self._match_then_eat(',')

        self._eat(TokenKind.IN)
        body = self._parse_expression()
        return VarIn(vars, body)

    # binoprhs ::= (<binop> primary)*
    def _parse_binop_rhs(self, expr_prec, lhs):
        """Parse the right-hand-side of a binary expression.
        expr_prec: minimal precedence to keep going (precedence climbing).
        lhs: AST of the left-hand-side.
        """
        while True:
            cur_prec, cur_assoc = self.binop_info()
            # If this is a binary operator with precedence lower than the
            # currently parsed sub-expression, bail out. If it binds at least
            # as tightly, keep going.
            # Note that the precedence of non-operators is defined to be -1,
            # so this condition handles cases when the expression ended.
            if cur_prec < expr_prec:
                return lhs
            op = self.cur_tok.text
            self._eat(TokenKind.OPERATOR) 
            rhs = self._parse_primary()

            next_prec, next_assoc = self.binop_info()
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

            if cur_prec == next_prec and next_assoc == binop.Associativity.RIGHT:
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
        op = self.cur_tok.text
        self._eat(TokenKind.OPERATOR)
        rhs = self._parse_primary()
        return Unary(op, rhs) 

    # prototype
    #   ::= id '(' id* ')'
    def _parse_prototype(self):
        idtok = self._eat(TokenKind.IDENTIFIER)

        self._eat('(')
        argnames = []
        while self._match(TokenKind.IDENTIFIER):
            argnames.append(self._eat().text)
        self._eat(')')

        if idtok.subkind == TokenKind.BINARY and len(argnames) != 2:
            self._raise('Binary operator should have 2 operands', idtok)
        elif idtok.subkind == TokenKind.UNARY and len(argnames) != 1:
            self._raise('Unary operator should have just one operand', idtok)

        return Prototype(idtok.text, argnames)

    # external ::= 'extern' prototype
    def _parse_external(self):
        self._eat(TokenKind.EXTERN) 
        return self._parse_prototype()

    # definition ::= 'def' prototype expression
    def _parse_definition(self):
        self._eat(TokenKind.DEF) 
        proto = self._parse_prototype()
        expr = self._parse_expression()
        return Function(proto, expr)

#---- Some unit tests ----#

import unittest
from lexing.source import Source

def parse_toplevel(buf, parser  = Parser()):
    return next(parser.parse_generator(Source("parsing tests", buf)))

class TestParser(unittest.TestCase):

    def _assert_ast(self, ast, expected_flattened_ast):
        self.assertEqual(ast.flatten(), expected_flattened_ast)

    def _assert_parse(self, codestr, expected_flattened_ast):
        self.assertEqual(
            parse_toplevel(codestr).flatten(), 
            expected_flattened_ast)

    def _assert_body(self, toplevel, expected):
        """Assert the flattened body of the given toplevel function"""
        self.assertIsInstance(toplevel, Function)
        self.assertEqual(toplevel.body.flatten(), expected)

    def test_basic(self):
        ast = parse_toplevel('2')
        self.assertIsInstance(ast, Number)
        self.assertEqual(ast.val, '2')

    def test_basic_with_flattening(self):
        self._assert_parse('2', ['Number', '2'])
        self._assert_parse('foobar', ['Variable', 'foobar'])

    def test_expr_singleprec(self):
        self._assert_parse('2+ 3-4',
            ['Binary',
                '-', ['Binary', '+', ['Number', '2'], ['Number', '3']],
                ['Number', '4']])

    def test_expr_multiprec(self):
        self._assert_parse('2+3*4-9',
            ['Binary', '-',
                ['Binary', '+',
                    ['Number', '2'],
                    ['Binary', '*', ['Number', '3'], ['Number', '4']]],
                ['Number', '9']])

    def test_expr_parens(self):
        self._assert_parse('2*(3-4)*7',
            ['Binary', '*',
                ['Binary', '*',
                    ['Number', '2'],
                    ['Binary', '-', ['Number', '3'], ['Number', '4']]],
                ['Number', '7']])

    def test_externals(self):
        self._assert_parse('extern sin(arg)', ['Prototype', 'sin', ['arg']])

        self._assert_parse('extern Foobar(nom denom abom)',
            ['Prototype', 'Foobar', ['nom', 'denom', 'abom']])

    def test_funcdef(self):
        self._assert_parse('def foo(x) 1 + bar(x)',
            ['Function', ['Prototype', 'foo', ['x']],
                ['Binary', '+',
                    ['Number', '1'],
                    ['Call', 'bar', [['Variable', 'x']]]]])

    def test_unary(self):
        p = Parser()
        ast = parse_toplevel('def unary!(x) 0 - x', p)
        self.assertIsInstance(ast, Function)
        proto = ast.proto
        self.assertIsInstance(proto, Prototype)
        self.assertEqual(proto.name, 'unary!')

        ast = parse_toplevel('!a + !b - !!c', p)
        self._assert_ast(ast,
            ['Binary', '-',
                ['Binary', '+',
                    ['Unary', '!', ['Variable', 'a']],
                    ['Unary', '!', ['Variable', 'b']]],
                ['Unary', '!', ['Unary', '!', ['Variable', 'c']]]])

    def test_binary_op(self):
        ast = parse_toplevel('def binary$ (a b) a + b')
        self.assertIsInstance(ast, Function)
        proto = ast.proto
        self.assertIsInstance(proto, Prototype)
        self.assertEqual(proto.name, 'binary$')


    def test_binop_right_associativity(self):
        self._assert_parse('x = y = 10 + 5',
            ['Binary', '=',
                ['Variable', 'x'],
                ['Binary', '=',
                    ['Variable', 'y'],
                    ['Binary', '+', ['Number', '10'], ['Number', '5']]]])

    def test_var(self):
        self._assert_parse('var x in x',
            ['VarIn', 
                [('x', None)],
                ['Variable', 'x']])

        self._assert_parse('var x y = 10 in x',
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
     
