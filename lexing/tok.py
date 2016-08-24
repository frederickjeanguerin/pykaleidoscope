from enum import *
from .mixin import * 
from .span import Span
from .line import Line

@unique
class TokenKind(Enum):
    IDENTIFIER = -4
    NUMBER = -5
    OPERATOR = -6

    # Virtual Tokens are positive
    EOF = +1
    
    # Keywords are less than -100
    DEF = -101
    EXTERN = -102
    IF = -103
    THEN = -104
    ELSE = -105
    FOR = -106
    IN = -107
    BINARY = -108
    UNARY = -109
    VAR = -110

    @property
    def is_keyword(self):
        return self.value < 100

    @property    
    def is_virtual(self):
        return self.value > 0

    @staticmethod
    def get_keyword(keywordname):
        """ Returns the TokenKind of a keywordname or None if not found"""
        try:
            kind = TokenKind[keywordname.upper()]
            if kind.value < -100: 
                return kind
        except KeyError:
            pass
        return None    


class Token(EqualityMixin, StrMixin):
    """ Token descriptor : immutable """

    def __init__(self, kind, span, line, subkind = None):
        self.kind = kind
        self.span = span
        self.line = line
        self.subkind = subkind

    @property
    def eof(self):
        return self.kind is TokenKind.EOF    

    @property
    def value(self):
        return self.span.text    

    @property
    def text(self):
        return self.span.text    

    @property
    def len(self):
        return self.span.len    

    @property
    def lineno(self):
        return self.line.no    

    @property
    def indent(self):
        """ Indentation of the line on which sits that token.
            Indentation of EOF is always -1.
        """
        if self.eof :
            return -1
        else:
            return self.line.indentsize    

    @property
    def linein(self):
        """ Line number on which sits the token.
            This number is always lastline + 10 for EOF.
        """
        if self.eof :
            return self.lineno + 10
        else:
            return self.lineno    

    @property
    def colno(self):
        return self.span.start - self.line.pos + 1    

    @property
    def endcolno(self):
        return self.span.stop - self.line.pos + 1   

    def __str__(self):
        if self.kind.is_virtual:
            return self.kind.name
        return self.text    

    def match(self, attribute):
        """Return true if the token matches with the given attribute"""
        return attribute in (self.kind, self.text, self.subkind)        

    @staticmethod
    def mock(kind = TokenKind.IDENTIFIER, text = 'mocked_token_text', subkind = None):
        return Token(kind, Span.mock(text), Line.mock(text), subkind) 

#---- Some unit tests ----#

import unittest

class TestTok(unittest.TestCase):

    def test_token_kind(self):
        self.assertTrue(TokenKind.IF.is_keyword)
        self.assertTrue(TokenKind.EOF.is_virtual)

    def test_token_str(self):
        self.assertEqual(str(Token.mock(text = "some_text")), "some_text")
        self.assertEqual(str(Token.mock(TokenKind.EOF, '')), "EOF")

    def test_get_keyword(self):
        self.assertEqual(TokenKind.get_keyword('if'), TokenKind.IF)
        self.assertEqual(TokenKind.get_keyword('not a token'), None)

    def test_token_equality(self):
        self.assertEqual(Token.mock(), Token.mock())

    def test_token_match(self):
        t = Token.mock(TokenKind.IDENTIFIER, 'binary+', TokenKind.BINARY)
        self.assertTrue(t.match(TokenKind.IDENTIFIER))
        self.assertTrue(t.match(TokenKind.BINARY))
        self.assertTrue(t.match('binary+'))

if __name__ == '__main__':
    unittest.main()