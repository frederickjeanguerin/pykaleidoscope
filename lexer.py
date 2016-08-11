from enum import * 
from collections import namedtuple

# Each token is a tuple of kind and value. kind is one of the enumeration values
# in TokenKind. value is the textual value of the token in the input.
@unique
class TokenKind(Enum):
    EOF = -1
    IDENTIFIER = -4
    NUMBER = -5
    OPERATOR = -6
    # Keywords are less than -100
    DEF = -101
    EXTERN = -102
    IF = -103
    THEN = -104
    ELSE = -105
    FOR = -106
    IN = -107


Token = namedtuple('Token', 'kind value')

def get_keyword(name):
    try:
        kind = TokenKind[name.upper()]
        if kind.value < -100: 
            return kind
    except KeyError:
        pass
    return None    

class Lexer(object):
    """Lexer for Kaleidoscope.
    Initialize the lexer with a string buffer. tokens() returns a generator that
    can be queried for tokens. The generator will emit an EOF token before
    stopping.
    """
    def __init__(self, buf):
        assert len(buf) >= 1
        self.buf = buf
        self.pos = 0
        self.lastchar = self.buf[0]

    def tokens(self):
        while self.lastchar:
            # Skip whitespace
            while self.lastchar.isspace():
                self._advance()
            # Identifier or keyword
            if self.lastchar.isalpha():
                id_str = ''
                while self.lastchar.isalnum():
                    id_str += self.lastchar
                    self._advance()
                if get_keyword(id_str):
                    yield Token(kind=get_keyword(id_str), value=id_str)
                else:
                    yield Token(kind=TokenKind.IDENTIFIER, value=id_str)
            # Number
            elif self.lastchar.isdigit() or self.lastchar == '.':
                num_str = ''
                while self.lastchar.isdigit() or self.lastchar == '.':
                    num_str += self.lastchar
                    self._advance()
                yield Token(kind=TokenKind.NUMBER, value=num_str)
            # Comment
            elif self.lastchar == '#':
                self._advance()
                while self.lastchar and self.lastchar not in '\r\n':
                    self._advance()
            elif self.lastchar:
                # Some other char
                yield Token(kind=TokenKind.OPERATOR, value=self.lastchar)
                self._advance()
        yield Token(kind=TokenKind.EOF, value='')

    def _advance(self):
        try:
            self.pos += 1
            self.lastchar = self.buf[self.pos]
        except IndexError:
            self.lastchar = ''

#---- Some unit tests ----#

import unittest

class TestLexer(unittest.TestCase):
    def _assert_toks(self, toks, kinds):
        """Assert that the list of toks has the given kinds."""
        self.assertEqual([t.kind.name for t in toks], kinds)

    def test_lexer_simple_tokens_and_values(self):
        l = Lexer('a+1')
        toks = list(l.tokens())
        self.assertEqual(toks[0], Token(TokenKind.IDENTIFIER, 'a'))
        self.assertEqual(toks[1], Token(TokenKind.OPERATOR, '+'))
        self.assertEqual(toks[2], Token(TokenKind.NUMBER, '1'))
        self.assertEqual(toks[3], Token(TokenKind.EOF, ''))

        l = Lexer('.1519')
        toks = list(l.tokens())
        self.assertEqual(toks[0], Token(TokenKind.NUMBER, '.1519'))

    def test_token_kinds(self):
        l = Lexer('10.1 def der extern foo (')
        self._assert_toks(
            list(l.tokens()),
            ['NUMBER', 'DEF', 'IDENTIFIER', 'EXTERN', 'IDENTIFIER',
             'OPERATOR', 'EOF'])

        l = Lexer('+- 1 2 22 22.4 a b2 C3d')
        self._assert_toks(
            list(l.tokens()),
            ['OPERATOR', 'OPERATOR', 'NUMBER', 'NUMBER', 'NUMBER', 'NUMBER',
             'IDENTIFIER', 'IDENTIFIER', 'IDENTIFIER', 'EOF'])

    def test_skip_whitespace_comments(self):
        l = Lexer('''
            def foo # this is a comment
            # another comment
            \t\t\t10
            ''')
        self._assert_toks(
            list(l.tokens()),
            ['DEF', 'IDENTIFIER', 'NUMBER', 'EOF'])


#---- Typical example use ----#

if __name__ == '__main__':

    import sys
    program = 'def bina(a b) a + b'
    if len(sys.argv) > 1 :
        program = ' '.join(sys.argv[1:])
    print("\nPROGRAM: ", program)    
    print("\nTOKENS: ")    
    lexer = Lexer(program)
    for token in lexer.tokens():
        print("  ", token.kind.name, token.value)
