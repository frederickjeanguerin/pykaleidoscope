from lexing.lexer import tokens_from, Token, TokenKind, Span

class ParseError(Exception): 
    """ Expecting two arguments: (message, token). """
    pass

class TokenFeeder :

    def __init__(self, source):
        self._lexer = tokens_from(source)
        self._previous = None
        self._current = None
        self._next = next(self._lexer)
        self._fetch()       

    def _fetch(self):    
        """Fetch the next token from the token source."""    
        self._current = self._next
        if not self._current.eof:    
            self._next = next(self._lexer)

    def _update(self):
        """Update previous, current and next token."""    
        self._previous = self._current
        self._fetch()        

    @property
    def current(self):
        return self._current    

    def eat(self, attribute = None):
        """Consume and return the current token; 
        If attribute present, verify that the current token matches it. 
        """
        if attribute:
            self.expect(attribute)
        self._update()
        return self._previous

    def match(self, token_attribute):
        """Returns True the the current token matches agains the attribute."""
        return self._current.match(token_attribute)

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

    def throw(self, message, token = None):
        """Raise a parse error, passing it a message and the current token"""
        raise ParseError(message, token or self.currrent)

