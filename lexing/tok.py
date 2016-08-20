from enum import *
from .mixin import * 
from . import span

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
    BINARY = -108
    UNARY = -109
    VAR = -110

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

    def __init__(self, kind, span, subkind = None):
        self.kind = kind
        self.span = span
        self.subkind = subkind    

    @property
    def value(self):
        return self.span.text    

    @property
    def text(self):
        return self.span.text    

    @property
    def len(self):
        return self.span.len    


def mock(kind = TokenKind.IDENTIFIER, identifierstr = 'mocked_token_text'):
    return Token(kind, span.mock(identifierstr)) 

#---- Some unit tests ----#

import unittest

class TestTok(unittest.TestCase):

    def test_get_keyword(self):
        self.assertEqual(TokenKind.get_keyword('if'), TokenKind.IF)
        self.assertEqual(TokenKind.get_keyword('not a token'), None)

    def test_token_equality(self):
        self.assertEqual(mock(), mock())

if __name__ == '__main__':
    unittest.main()