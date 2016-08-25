
from .tok import Token, TokenKind
from .char_feeder import CharFeeder
from .line import Line



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
        # A new token starts here    
        token_line = feeder.line
        token_pos = feeder.pos   
        # Identifier or keyword
        if feeder.current.isalpha():
            while feeder.current.isalnum() or feeder.current == '_':
                feeder.next()
            token_text = source[token_pos:feeder.pos]
            kind = TokenKind.get_keyword(token_text)
            # Operator identifier
            if kind in [TokenKind.BINARY, TokenKind.UNARY]:
                if feeder.is_empty() or feeder.current.isspace():
                    yield Token(TokenKind.IDENTIFIER, token_text, token_pos, token_line)
                else :
                    feeder.next()  # Add operator to identifier
                    yield Token(TokenKind.IDENTIFIER, token_text + feeder.current, token_pos, token_line, kind)
            # Keyword         
            elif kind:
                yield Token(kind, token_text, token_pos, token_line)
            # Identifier    
            else:
                yield Token(TokenKind.IDENTIFIER, token_text, token_pos, token_line)
        # Number
        elif feeder.current.isdigit() or feeder.current == '.':
            while feeder.current.isdigit() or feeder.current == '.':
                feeder.next()
            yield Token(TokenKind.NUMBER, source[token_pos:feeder.pos], token_pos, token_line )
        # Comment
        elif feeder.current == '#':
            while feeder.current and feeder.current not in '\r\n':
                feeder.next()
        # Operator or operator special identifier
        elif feeder.current:
            feeder.next()
            yield Token(TokenKind.OPERATOR, source[token_pos:feeder.pos], token_pos, token_line )

    yield Token(TokenKind.EOF, '<EOF>', feeder.pos, feeder.line )


#---- Some unit tests ----#

import unittest

def _lex(codestr, _lambda = lambda x : x):
    return [_lambda(tok) for tok in tokens_from(codestr)]

def _lex_kind(codestr):
    return _lex(codestr, lambda x : x.kind.name)

def _lex_text(codestr):
    return _lex(codestr, lambda x : x.text)

class TestLexer(unittest.TestCase):

    def _assert_sametok(self, tok1, tok2):
        self.assertEqual(tok1.text, tok2.text)
        self.assertEqual(tok1.kind, tok2.kind)

    def _assert_kinds(self, codestr, kinds):
        self.assertListEqual(_lex_kind(codestr), kinds + ['EOF'])

    def _assert_texts(self, codestr, texts):
        self.assertListEqual(_lex_text(codestr), texts + ['<EOF>'])

    def _assert_lex(self, codestr, expected_tokens, lex = _lex):
        tokens = _lex(codestr)
        self.assertEqual(len(tokens), len(expected_tokens) + 1)
        for i, tok in enumerate(tokens[:-2]):
            self.assertEqual(tok.kind.name, expected_tokens[i][0])
            self.assertEqual(tok.text, expected_tokens[i][1])
            if len(expected_tokens[i]) == 3:
                self.assertEqual(tok.subkind, expected_tokens[i][2])
        self.assertTrue(tokens[-1].eof)    

    def test_lexer_empty(self):
        self.assertEqual(_lex_kind(''), ['EOF'])

    def test_lexer_number(self):
        self._assert_kinds('1', ['NUMBER'])
        self._assert_texts('1', ['1'])
        self._assert_kinds('12', ['NUMBER'])
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
             'OPERATOR'])

        self._assert_kinds(
            '+- 1 2 22 22.4 a b2 C3d',
            ['OPERATOR', 'OPERATOR', 'NUMBER', 'NUMBER', 'NUMBER', 'NUMBER',
             'IDENTIFIER', 'IDENTIFIER', 'IDENTIFIER'])

    def test_skip_whitespace_comments(self):
        self._assert_kinds(
            '''
            def foo # this is a comment
            # another comment
            \t\t\t10
            ''',
            ['DEF', 'IDENTIFIER', 'NUMBER'])

    def test_lineinfo(self):
        toks = _lex('   line1   \n   line2  line2   ')
        self.assertEqual(toks[1].text, 'line2')
        self.assertEqual(toks[1].lineno, 2)
        self.assertEqual(toks[1].colno, 4)
        self.assertEqual(toks[1].indent, 3)
        self.assertEqual(toks[2].indent, 3)


#---- Run module tests ----#

if __name__ == '__main__':
    unittest.main()

