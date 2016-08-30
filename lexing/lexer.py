
from .char_feeder import *

_PUNCTUATORS = "()[]{}.,;:#_'\""

def is_operator_char(char):
    return not ( char.isalnum()
        or char.isspace()
        or char in _PUNCTUATORS )

def tokens_from(source):
    """Lexer for Kaleidoscope.
    Returns a generator that can be queried for tokens. 
    The generator will emit an EOF token before stopping.
    """

    f = CharFeeder(source)      
    while not f.is_empty():
        # Skip whitespace
        while f.current.isspace():
            f.next()
        if f.is_empty() :
            break;    
        # Else a new token starts here    
        f.start_token()
        # LLVM Identifier 
        if f.current == "%":
            iden_type = LlvmIdentifier
            f.next()
        else:
            iden_type = Identifier    
        # Identifier 
        if f.current.isalpha():
            while f.current.isalnum() or f.current == '_':
                f.next()
            yield f.new_token(iden_type)
            continue;
        else:
            f.rebase()    
        # Number
        if f.current.isdigit() or f.current == '.':
            while f.current.isdigit() or f.current == '.':
                f.next()
            yield f.new_token(Number)
        # Line Comment --> skip
        elif f.current == '#':
            while f.current and f.current not in '\r\n':
                f.next()
        # Operator 
        elif is_operator_char(f.current):
            while is_operator_char(f.current):
                f.next()
            yield f.new_token(Operator)
        # Punctuator
        else:    
            f.next()
            yield f.new_token(Punctuator)

    # Yield a terminal EOF marker        
    f.start_token()
    yield f.new_token(EOF)




