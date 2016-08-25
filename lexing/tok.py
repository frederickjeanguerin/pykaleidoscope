from enum import *
from collections import namedtuple
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




class Token(namedtuple('_Token', 'kind text pos line')):
    """ 
        A token from the lexing phase of compilation. 
    
        kind: TokenKind
        text: str
        pos: offset of the token in the source code, starting at 0
        line: Line on which sits the token   
    """

    def __new__(cls, kind, text, pos, line, subkind = None):
        self = super(Token,cls).__new__(cls, kind, text, pos, line)
        self.subkind = subkind
        return self

    def __init__(cls, kind, text, pos, line, subkind = None):
        # Initialisation already done in __new__
        pass


    @property
    def eof(self):
        """ True if token is and end of file marker, 
            i.e. the last token from source"""
        return self.kind is TokenKind.EOF    

    @property
    def value(self):
        "Deprecated: Use text property instead"
        return self.text    

    @property
    def len(self):
        return len(self.text)    

    @property
    def lineno(self):
        return self.line.no    

    @property
    def colno(self):
        return self.pos - self.line.pos + 1

    @property
    def source(self):
        return self.line.source    

    def __str__(self):
        return self.text    

    def match(self, attribute):
        """Return true if the token matches with the given attribute"""
        return attribute in (self.kind, self.text, self.subkind)        

    @staticmethod
    def mock(kind = TokenKind.IDENTIFIER, text = 'mocked_token_text', subkind = None):
        return Token(kind, text, 0, Line.mock(text), subkind) 

#---- Some unit tests ----#

import unittest

class TestTok(unittest.TestCase):

    def test_token_kind(self):
        self.assertTrue(TokenKind.IF.is_keyword)
        self.assertTrue(TokenKind.EOF.is_virtual)

    def test_token_str(self):
        self.assertEqual(str(Token.mock(text = "some_text")), "some_text")

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
        self.assertFalse(t.match(TokenKind.IF))
        self.assertFalse(t.match(TokenKind.UNARY))
        self.assertFalse(t.match('binary'))

if __name__ == '__main__':
    unittest.main()