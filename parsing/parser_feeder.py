from .indenter import *
from code_error import *

class ParseError(CodeError): 
    def __init__(self, token, msg = "Unexpected token"):
        assert token.match(Token)
        self.token = token 
        self.msg = msg 

class ParserFeeder :

    def __init__(self, stmt):
        self._previous = None
        self._current = None
        self._next = None
        self._tokblocks = (tocblock for tocblock in stmt.tokblocks)
        self._fetch()
        self._fetch()

    def _fetch(self):    
        """Fetch the next token from the token source."""
        self._previous = self._current
        self._current = self._next    
        try :    
            self._next = next(self._tokblocks)
        except StopIteration:
            self._next = None    

    @property
    def current(self):
        return self._current    

    def eat(self, attribute = None):
        """Consume and return the current token; 
        If attribute present, verify that the current token matches it. 
        """
        if attribute:
            self.expect(attribute)
        current = self._current
        self._fetch()
        return current

    @property    
    def is_left_glued(self):
        """True if the current token is a glued to the previous one"""
        return self._previous and self._current and self._previous.endpos == self._current.pos

    @property    
    def is_right_glued(self):
        """True if the current token is a glued to the next one"""
        return self._next and self._current and self._current.endpos == self._next.pos

    @property    
    def is_glued(self):
        """True if the current token is a glued to the previous and next one"""
        return self.is_left_glued and self.is_right_glued

    @property    
    def is_unglued(self):
        """ True if the current token is a not glued at all 
            to the previous or next one"""
        return not self.is_left_glued and not self.is_right_glued


    def match(self, attribute):
        """Returns True the the current token matches agains the attribute."""
        return self._current is attribute \
            or self.current and self.current.match(attribute)

    def expect(self, token_attribute):
        """Verify the current token against the given attribute"""
        if not self.match(token_attribute):
            throw('Expected ' + str(token_attribute))

    def match_then_eat(self, token_attribute):
        """Return true if the current token matches with the given attribute, eating that token by the way"""
        if self.match(token_attribute):
            self.eat()
            return True
        return False            

    def throw(self, message = "Unexpected!", tokblock = None):
        """Raise a parse error, passing it a message and the current tokblock"""
        raise ParseError(message, tokblock.first_token or self.current.first_token)

