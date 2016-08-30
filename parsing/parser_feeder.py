from .indenter import *
from code_error import *

class ParseError(CodeError): 
    def __init__(self, token, msg = "Unexpected token"):
        assert token.match(Token)
        self.token = token 
        self.msg = msg 

    def __str__(self):
        return self.msg
            

class ParserFeeder :

    def __init__(self, stmt):
        self.previous = None
        self.current = None
        self.next = None
        self._tokblocks = (tocblock for tocblock in stmt.tokblocks)
        self._fetch()
        self._fetch()

    def _fetch(self):    
        """Fetch the next token from the token source."""
        self.previous = self.current
        self.current = self.next    
        try :    
            self.next = next(self._tokblocks)
        except StopIteration:
            self.next = None    

    def eat(self, attribute = None):
        """Consume and return the current token; 
        If attribute present, verify that the current token matches it. 
        """
        if attribute:
            self.expect(attribute)
        current = self.current
        self._fetch()
        return current

    @property    
    def is_left_glued(self):
        """True if the current token is a glued to the previous one"""
        return self.previous and self.current and self.previous.endpos == self.current.pos

    @property    
    def is_right_glued(self):
        """True if the current token is a glued to the next one"""
        return self.next and self.current and self.current.endpos == self.next.pos

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
        return self.current is attribute \
            or self.current and self.current.match(attribute)

    def expect(self, token_attribute):
        """Verify the current token against the given attribute"""
        if not self.match(token_attribute):
            self.throw('Expected ' + str(token_attribute) + ' after ' + self.previous.error_str, self.previous)

    def match_then_eat(self, token_attribute):
        """Return true if the current token matches with the given attribute, eating that token by the way"""
        if self.match(token_attribute):
            self.eat()
            return True
        return False            

    def throw(self, message = None, tokblock = None):
        """Raise a parse error, passing it a message and the current tokblock"""
        token = (tokblock and tokblock.first_token) or self.current.first_token
        message = message or "Unexpected " + token.error_str
        raise ParseError( token , message)

