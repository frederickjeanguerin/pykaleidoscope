
from collections import namedtuple
from .line import *

class Token(namedtuple('_Token', 'text pos line')):
    """ 
        A token from the lexing phase of compilation. 
    
        text: the token string
        pos: offset of the token in the source code, starting at 0
        line: Line on which sits the token   
    """

    def __init__(cls, text, pos, line):
        # Initialisation already done in namedtuple.__new__
        pass


    @property
    def endpos(self):
        """ Token endind position + 1 in source code"""
        return self.pos + self.len    

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

    @property
    def first_token(self):
        """ When tokens are considered expressions in the AST"""
        return self        

    @property
    def last_token(self):
        """ When tokens are considered expressions in the AST"""
        return self    

    def __str__(self):
        return self.text    

    def _match_attr(self, attribute):
        """Return true if the token matches the given attribute"""
        return isinstance(attribute, type) and isinstance(self, attribute) or self.text == attribute            

    def match(self, *attributes):
        """Return true if the token matches with all the given attributes"""
        return all( (self._match_attr(attr) for attr in attributes )  )  


    @classmethod
    def mock(cls, text = 'mocked_token_text'):
        return cls.__new__(cls, text, 0, Line.mock(text)) 




# ------------- Derived Classes ---------  i.e. subtoken types

class EOF(Token):

    def __str__(self):
        return "<EOF>"    


class VisibleToken(Token):
    """ Visible or real token, compared to a virtual token like EOF """
    pass

class Punctuator(VisibleToken):
    """ Any char or group of char that influence the parsing of the code.
        These includes all operators, all keywords, and all other 
        punctuation marks like comas, colon, semi-colon, parenthesis, etc.  
    """
    pass

class Operator(Punctuator):
    pass

class Wordlike(VisibleToken):
    ''' Wordlikes are tokens that are acted upon by punctuators.
        They comprise everything else, like Identifiers, numbers, strings, etc. 
    '''
    pass

class Number(Wordlike):
    pass

class Identifier(Wordlike):
    pass

class OperatorIdenfier(Identifier):
    ''' Every operator has an underlying associated identifier, 
        E.g. binary + has identifier ___+___ 
    '''
    pass

