
from .tokens import *

class CharFeederIsEmpty(Exception):
    pass

class BasicCharFeeder:

    def __init__(self, source):
        self.source = source
        self.pos = -1
        self.current = None
        self.next()        

    def is_empty(self):
        "True if feeder has no more character available"
        return self.pos == len(self.source)

    def is_last(self):
        "True if feeder is positioned at the last character"
        return self.pos == len(self.source) - 1

    def next(self):
        """Advance the feeder to the next available char."""

        # If feeder already exhauted, raise an error
        if self.is_empty():
            raise CharFeederIsEmpty()

        self.pos += 1    

        if self.is_empty():
            self.current = ''
            return

        self.current = self.source[self.pos]


class LineCharFeeder (BasicCharFeeder):

    def __init__(self, source):
        self.lineno = 1
        self.line = Line(self.lineno, 0, source)
        super().__init__(source)

    def next(self):
        """
        Advance the feeder to the next available char, 
        eating up indentation if any.

        That char is available in 'current'.
        The line to which belongs this current char is available in 'line'. 
        
        """

        # if ending a line 
        if self.current == '\n' or self.is_last() :
            # Finish current line initialization
            self.line.endpos = self.pos + 1

        # If starting a new line
        if self.current == '\n' :    
            self.lineno += 1
            self.line = Line(self.lineno, self.pos + 1, self.source)

        super().next()

        # if just starting a line, eat up indentation    
        if self.pos == self.line.pos:
            while self.current.isspace() and not self.current == '\n':
                # TODO : Warn here for tabulations if any
                super().next()
            self.line.indentpos = self.pos

class CharFeeder(LineCharFeeder):

    def __init__(self, source):
        super().__init__(source)
        self.tokenpos = None 

    def start_token(self):
        """Set the starting mark for a new token"""
        self.tokenpos = self.pos

    def new_token(self, cls):        
        """Return a new token starting from tokenpos"""
        return Token.__new__(cls, self.source[self.tokenpos:self.pos], self.tokenpos, self.line)

    def rebase(self):
        "Rebase the feeder to the position where a start_token was done"    
        assert self.tokenpos is not None
        assert "\n" not in self.source[self.tokenpos:self.pos]
        self.pos = self.tokenpos
        self.current = self.source[self.pos]
