
from .tok import Token, TokenKind
from .char_feeder import CharFeeder

def tokens_from(source):
    """Lexer for Kaleidoscope.
    Returns a generator that can be queried for tokens. 
    The generator will emit an EOF token before stopping.
    """

    feeder = CharFeeder(source)
        
    while not feeder.is_empty():
        # Skip whitespace
        while feeder.current.isspace():
            feeder.next()
        # A new token ahead so start recording for a token span    
        feeder.start_span()
        line = feeder.line
        # Identifier or keyword
        if feeder.current.isalpha():
            while feeder.current.isalnum() or feeder.current == '_':
                feeder.next()
            span = feeder.get_span()
            kind = TokenKind.get_keyword(span.text)
            # Operator identifier
            if kind in [TokenKind.BINARY, TokenKind.UNARY]:
                if feeder.is_empty() or feeder.current.isspace():
                    yield Token(TokenKind.IDENTIFIER, span, line)
                else :
                    feeder.next()  # Add operator to identifier
                    yield Token(TokenKind.IDENTIFIER, feeder.get_span(), line, kind)
            # Keyword         
            elif kind:
                yield Token(kind, span, line)
            # Identifier    
            else:
                yield Token(TokenKind.IDENTIFIER, span, line)
        # Number
        elif feeder.current.isdigit() or feeder.current == '.':
            while feeder.current.isdigit() or feeder.current == '.':
                feeder.next()
            yield Token(TokenKind.NUMBER, feeder.get_span(), line )
        # Comment
        elif feeder.current == '#':
            while feeder.current and feeder.current not in '\r\n':
                feeder.next()
        # Operator or operator special identifier
        elif feeder.current:
            feeder.next()
            yield Token(TokenKind.OPERATOR, feeder.get_span(),  line )

    feeder.start_span() 
    EOF_Token = Token(TokenKind.EOF, feeder.get_span(), feeder.line )

    yield EOF_Token 


#---- Some unit tests ----#

import unittest
from .source import Source
from .span import Span
from .line import Line

def _lex(codestr):
    src = Source.mock(codestr)
    return list(tokens_from(src)), src

class TestLexer(unittest.TestCase):

    def _assert_sametok(self, tok1, tok2):
        # We need to compare text before to generate 
        # the private _text field in both objects
        self.assertEqual(tok1.text, tok2.text)
        self.assertEqual(tok1.kind, tok2.kind)

    def _assert_lex(self, codestr, expected_tokens):
        tokens, src = _lex(codestr)
        self.assertEqual(len(tokens), len(expected_tokens) + 1)
        for i, tok in enumerate(tokens[:-2]):
            self.assertEqual(tok.kind.name, expected_tokens[i][0])
            self.assertEqual(tok.text, expected_tokens[i][1])
            if len(expected_tokens[i]) == 3:
                self.assertEqual(tok.subkind, expected_tokens[i][2])
                
        self._assert_sametok(tokens[-1], Token.mock(TokenKind.EOF, ''))    

    def _assert_kinds(self, codestr, kinds):
        """Assert that the list of toks has the given kinds."""
        toks, src = _lex(codestr)
        self.assertEqual([t.kind.name for t in toks], kinds)

    def test_lexer_empty(self):
        toks, src = _lex('')
        self.assertEqual(toks[0], Token(TokenKind.EOF, Span(0,0,src), Line(1,0, src)))

    def test_lexer_number(self):
        self._assert_lex('.1519', [('NUMBER', '.1519')])
        self._assert_lex('23.15', [('NUMBER', '23.15')])
        self._assert_lex('1519.', [('NUMBER', '1519.')])

    def test_lexer_iden(self):
        self._assert_lex('an_identifier', [('IDENTIFIER', 'an_identifier')])
        
    def test_lexer_keyword(self):
        self._assert_lex('if', [('IF', 'if')])

    def test_lexer_operator_iden(self):
        self._assert_lex('unary+', [('IDENTIFIER', 'unary+', TokenKind.UNARY)])
        self._assert_lex('binary*', [('IDENTIFIER', 'binary*', TokenKind.BINARY)])
        self._assert_lex('unary', [('IDENTIFIER', 'unary', None)])
        self._assert_lex('binary', [('IDENTIFIER', 'binary', None)])

    def test_lexer_operator(self):
        self._assert_lex('+', [('OPERATOR', '+')])
        self._assert_lex(' + ', [('OPERATOR', '+')])
                
    def test_lexer_simple_expr(self):
        self._assert_lex('a+1', [('IDENTIFIER', 'a'),('OPERATOR', '+'),('NUMBER','1')])

    def test_token_kinds(self):
        self._assert_kinds(
            '10.1 def der extern foo (',
            ['NUMBER', 'DEF', 'IDENTIFIER', 'EXTERN', 'IDENTIFIER',
             'OPERATOR', 'EOF'])

        self._assert_kinds(
            '+- 1 2 22 22.4 a b2 C3d',
            ['OPERATOR', 'OPERATOR', 'NUMBER', 'NUMBER', 'NUMBER', 'NUMBER',
             'IDENTIFIER', 'IDENTIFIER', 'IDENTIFIER', 'EOF'])

    def test_skip_whitespace_comments(self):
        self._assert_kinds(
            '''
            def foo # this is a comment
            # another comment
            \t\t\t10
            ''',
            ['DEF', 'IDENTIFIER', 'NUMBER', 'EOF'])

    def test_lineinfo(self):
        toks, src = _lex('   line1   \n   line2   ')
        self.assertEqual(toks[1].text, 'line2')
        self.assertEqual(toks[1].lineno, 2)
        self.assertEqual(toks[1].colno, 4)



#---- Run module tests ----#

if __name__ == '__main__':
    unittest.main()
