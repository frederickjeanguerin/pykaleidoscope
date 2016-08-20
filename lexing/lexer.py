
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
        # A new token ahead so start recording for a span    
        feeder.start_span()
        # Identifier or keyword
        if feeder.current.isalpha():
            while feeder.current.isalnum() or feeder.current == '_':
                feeder.next()
            span = feeder.get_span()
            kind = TokenKind.get_keyword(span.text)
            # Operator identifier
            if kind in [TokenKind.BINARY, TokenKind.UNARY]:
                if feeder.is_empty() or feeder.current.isspace():
                    yield Token(TokenKind.IDENTIFIER, span)
                else :
                    feeder.next()  # Add operator to identifier
                    yield Token(TokenKind.IDENTIFIER, feeder.get_span(), kind)
            # Keyword         
            elif kind:
                yield Token(kind, span)
            # Identifier    
            else:
                yield Token(TokenKind.IDENTIFIER, span)
        # Number
        elif feeder.current.isdigit() or feeder.current == '.':
            while feeder.current.isdigit() or feeder.current == '.':
                feeder.next()
            yield Token(TokenKind.NUMBER, feeder.get_span())
        # Comment
        elif feeder.current == '#':
            while feeder.current and feeder.current not in '\r\n':
                feeder.next()
        # Operator or operator special identifier
        elif feeder.current:
            feeder.next()
            yield Token(TokenKind.OPERATOR, feeder.get_span())

    feeder.start_span()        
    yield Token(TokenKind.EOF, feeder.get_span())


#---- Some unit tests ----#

import unittest
from . import source
from .span import Span

def _lex(codestr):
    src = source.mock(codestr)
    return list(tokens_from(src)), src

class TestLexer(unittest.TestCase):

    def _assert_sametok(self, tok1, tok2):
        # We need to compare text before to generate 
        # the private _text field in both objects
        self.assertEqual(tok1.text, tok2.text)
        self.assertEqual(tok1, tok2)

    def _assert_toks(self, codestr, kinds):
        """Assert that the list of toks has the given kinds."""
        toks, src = _lex(codestr)
        self.assertEqual([t.kind.name for t in toks], kinds)

    def test_lexer_empty(self):
        toks, src = _lex('')
        self.assertEqual(toks[0], Token(TokenKind.EOF, Span(0,0,src)))

    def test_lexer_number(self):
        toks, src = _lex('.1519')
        self.assertEqual(toks[0], Token(TokenKind.NUMBER, Span(0,5,src)))

        toks, src = _lex('23.15')
        self.assertEqual(toks[0], Token(TokenKind.NUMBER, Span(0,5,src)))

        toks, src = _lex('1519.')
        self.assertEqual(toks[0], Token(TokenKind.NUMBER, Span(0,5,src)))
        self.assertEqual(toks[1], Token(TokenKind.EOF, Span(5,5,src)))
        
    def test_lexer_iden(self):
        toks, src = _lex('an_identifier')
        self._assert_sametok(toks[0], 
            Token(TokenKind.IDENTIFIER, Span(0,13,src)))
        
    def test_lexer_keyword(self):
        toks, src = _lex('if')
        self._assert_sametok(toks[0], Token(TokenKind.IF, Span(0,2,src)))

    def test_lexer_operator_iden(self):
        toks, src = _lex('unary+')
        self._assert_sametok(toks[0], Token(TokenKind.IDENTIFIER, Span(0,6,src), TokenKind.UNARY))

        toks, src = _lex('binary')
        self._assert_sametok(toks[0], Token(TokenKind.IDENTIFIER, Span(0,6,src)))

        toks, src = _lex(' binary ')
        self._assert_sametok(toks[0], Token(TokenKind.IDENTIFIER, Span(1,7,src)))

        toks, src = _lex(' binary* ')
        self._assert_sametok(toks[0], Token(TokenKind.IDENTIFIER, Span(1,8,src), TokenKind.BINARY))

    def test_lexer_operator(self):
        toks, src = _lex('+')
        self._assert_sametok(toks[0], Token(TokenKind.OPERATOR, Span(0,1,src)))
                
    def test_lexer_operator_with_spaces(self):
        toks, src = _lex(' + ')
        self._assert_sametok(toks[0], Token(TokenKind.OPERATOR, Span(1,2,src)))
        self._assert_sametok(toks[1], Token(TokenKind.EOF, Span(3,3,src)))
                
    def test_lexer_simple_expr(self):
        toks, src = _lex('a+1')
        self._assert_sametok(toks[0], Token(TokenKind.IDENTIFIER, Span(0, 1, src)))
        self._assert_sametok(toks[1], Token(TokenKind.OPERATOR, Span(1, 2, src)))
        self._assert_sametok(toks[2], Token(TokenKind.NUMBER, Span(2, 3, src)))
        self._assert_sametok(toks[3], Token(TokenKind.EOF, Span(3, 3, src)))

    def test_token_kinds(self):
        self._assert_toks(
            '10.1 def der extern foo (',
            ['NUMBER', 'DEF', 'IDENTIFIER', 'EXTERN', 'IDENTIFIER',
             'OPERATOR', 'EOF'])

        self._assert_toks(
            '+- 1 2 22 22.4 a b2 C3d',
            ['OPERATOR', 'OPERATOR', 'NUMBER', 'NUMBER', 'NUMBER', 'NUMBER',
             'IDENTIFIER', 'IDENTIFIER', 'IDENTIFIER', 'EOF'])

    def test_skip_whitespace_comments(self):
        self._assert_toks(
            '''
            def foo # this is a comment
            # another comment
            \t\t\t10
            ''',
            ['DEF', 'IDENTIFIER', 'NUMBER', 'EOF'])


#---- Typical example use ----#

if __name__ == '__main__':
    unittest.main()
