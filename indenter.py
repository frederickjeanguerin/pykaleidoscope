from collections import namedtuple
from lexing.lexer import tokens_from, Token, TokenKind



class IndentError(Exception): 
    """ Could not call this class IndentationError. """
    def __init__(self, line, msg = "Line is not properly indented"):
        self.line = line
        self.msg = msg 


class Block(namedtuple('_Indent', 'stmts')):

    __slots__ = ()

    def __init__(self, stmts): 
        pass

    @property    
    def indent(self):
        return self.stmts[0].indent

    def flatten(self):
        return [stmt.flatten() for stmt in self.stmts]

    def dump(self, indent_shift = 2, indent = 0):
        return "".join((stmt.dump(indent_shift, indent) for stmt in self.stmts))


class Stmt(namedtuple('_Stmt', 'tokblocks')):

    __slots__ = ()

    def __init__(self, tokblocks): 
        pass

    @property    
    def indent(self):
        return self.tokblocks[0].indent    

    def flatten(self):
        return [tb.text if isinstance(tb, Token) else tb.flatten() for tb in self.tokblocks]        

    def dump(self, indent_shift = 2, indent = 0):    
        s = ""
        has_dumped_block = False
        last_is_a_line = True
        first_on_line = True
        for tb in self.tokblocks:
            if isinstance(tb, Token):
                if first_on_line:
                    s += "  " * indent
                else:
                    s += " "
                s += tb.text
                first_on_line = False
                last_is_a_line = True
            else:                
                s += "\n" + tb.dump(indent_shift, indent + indent_shift)
                first_on_line = True
                has_dumped_block = True
                last_is_a_line = False

        if last_is_a_line:
            if has_dumped_block:
                s += "\n\n"
            else: 
                s += "\n"
        else : # last is a Block
            s += "\n"
        return s                        


class IndenterFeeder :

    def __init__(self, token_gen):
        """ token_gen is a token provider (generator) """
        self._tokens = token_gen
        self.previous = None
        self.current = next(self._tokens)

    def fetch(self):    
        """ Fetch the next token from the token source. """    
        self.previous = self.current
        if not self.previous.eof:    
            self.current = next(self._tokens)

    @property
    def lineno(self):
        """ Line no on which sits the current token.
            That line is always very far for EOF, because EOF 
            is always considered sitting on many lines 
            after the last real token.
        """
        if self.current.eof :
            return self.current.lineno + 10
        else:
            return self.current.lineno 

    @property
    def indent(self):
        """ Indentation of the line on which sits the current token.
            Indentation of EOF is always -1.
            Because EOF never match any indentation level.
        """
        if self.current.eof :
            return -1
        else:
            return self.current.line.indentsize                       

    @property
    def line_gap(self):
        """ Line gap between current and previous token
            0 if both are on the same line
            1 if current on the next line
            2 if there is a blank line in between, etc.
        """
        return self.lineno - self.previous.lineno        


def _parseBlock(feeder):
    assert not feeder.current.eof
    stmts = list()
    indent = feeder.indent 
    while feeder.indent == indent:
        stmts.append(_parseStmt(feeder))
    return Block(stmts)    

def _parseLine(feeder, tokblocks):
    # A line has at least one token
    assert not feeder.current.eof

    # Eat up the line
    lineno = feeder.lineno
    while feeder.lineno == lineno :
        tokblocks.append(feeder.current)
        feeder.fetch()


def _parseStmt(feeder):
    tokblocks = []
    indent = feeder.indent
    _parseLine(feeder, tokblocks)
    indent_shift = feeder.indent - indent
    # While there is indentation 
    while indent_shift > 0:  
        if indent_shift == 1 :
            raise IndentError(feeder.current.line, "Indentation must be greater than 1 space")
        elif indent_shift > 4 :
            raise IndentError(feeder.current.line, "Indentation must be no more than 4 spaces")
        # Parse the block    
        tokblocks.append(_parseBlock(feeder))

        # Check indentation after the block        
        indent_shift = feeder.indent - indent
        # If indentation not recovered, that is bad
        if indent_shift > 0 :
            raise IndentError(feeder.current.line)
        # If indentation is negative or same as before, 
        # but preceded by an empty line, the statement is terminated  
        if indent_shift < 0 or (indent_shift == 0 and feeder.line_gap >= 2):
            break
        # Otherwise, continue the statement with the new line.
        _parseLine(feeder, tokblocks)

        # Check indentation after the line
        indent_shift = feeder.indent - indent
        # If there is an unindent or if there is a blank line, end statement
        if indent_shift < 0 or (indent_shift == 0 and feeder.line_gap >= 2):
            break
        # If there is another line, then error
        if indent_shift == 0:
            raise IndentError(feeder.previous.line, "This line should be followed or preceded by a blanck line.")
        # Otherwise, there is a new indentation, so just loop
        assert indent_shift > 0    
        
    return Stmt(tokblocks)        
        

def stmts_from(token_gen):
    """ Parses a token stream (token generator from lexer) yielding Stmt one by one. """
    feeder = IndenterFeeder(token_gen)
    # The parser works with a real token in place, not EOF
    # So we just return in that case
    if feeder.current.eof:
        return
    # TODO warn if initial indent_level > 0
    indent = feeder.indent
    while feeder.indent == indent:
        yield _parseStmt(feeder)
    # If there are residual tokens,
    # It's because they are badly indented.    
    if not feeder.current.eof:
        raise IndentError(feeder.current.line)

def _parse(codestr):
    """ Returns the array of Stmt found in the code string as a giant Block """
    return Block([ stmt for stmt in stmts_from(tokens_from(codestr))])



import unittest


class TestIndenter(unittest.TestCase):

    def __assert(self, codestr, flattened):
        block = _parse(codestr)
        self.assertListEqual(block.flatten(), flattened)

    def __assert_dump(self, codestr, dumped = None):
        dumped = dumped or codestr
        block = _parse(codestr)
        self.assertEqual(block.dump().strip(), dumped.strip())

    def __assert_many_dumps(self, *many_codestr):
        for codestr in many_codestr:
            self.__assert_dump(codestr)

    def test_unindented(self):
        self.__assert("", [])
        self.__assert("1", [['1']])
        self.__assert("1 2", [['1', '2']])
        self.__assert("1 2\n3 4", [['1', '2'],['3', '4']])
        self.__assert("1 2\n  \n3 4  \n", [['1', '2'],['3', '4']])

    def test_indented(self):

        self.__assert("""
            if true
              be_foolish
            """, 
            [['if', 'true', 
                [['be_foolish']] 
            ]])

        self.__assert("""
            if true  
                be_foolish  
                and kool""", 
            [['if', 'true', 
                [['be_foolish'], 
                ['and', 'kool']] 
            ]])

    def test_indented_continuation(self):

        self.__assert("""
            if true
              be foolish
 
            else
              be sad  
            """, 
            [
                ['if', 'true', 
                    [['be', 'foolish']]],
                ['else',
                    [['be', 'sad']]]   
            ])

        self.__assert("""
            if true
              be foolish
            else
              be sad  
            """, 
            [
                ['if', 'true', 
                    [['be', 'foolish']],
                 'else',
                    [['be', 'sad']]]   
            ])

        self.__assert("""
            if true
              be foolish
            else
              be sad
            end    
            """, 
            [
                ['if', 'true', 
                    [['be', 'foolish']],
                 'else',
                    [['be', 'sad']],
                 'end' ]   
            ])


    def test_dump(self):

        self.__assert_many_dumps(
"",

"if",

"if true",

"""
if true
    be foolish
""",

"""
if true
    be foolish

else
    be sad  
""",

"""
if true
    be foolish
else
    be sad  
""",

"""
if true
    be foolish
else
    be sad
end

ok now be hungry      
""",

"""
if true
    be foolish
else
    be sad

ok now be hungry      
""",

"""
do
    be foolish
    be sad
while hungry
""",

"") 


    def test_indent_error(self):

        with self.assertRaises(IndentError) as err:
            _parse("""
                if true
                 ERROR this line not indented enough
                """)
        self.assertEqual(err.exception.line.no, 3)         


        with self.assertRaises(IndentError) as err:
            _parse("""
                if true
                            ERROR this line indented too much
                """)
        self.assertEqual(err.exception.line.no, 3)         
                 

        with self.assertRaises(IndentError) as err:
            _parse("""
                if true
            ERROR this line outdented
                """) 
        self.assertEqual(err.exception.line.no, 3)         


        with self.assertRaises(IndentError) as err:
            _parse("""
                if true
                    this line ok
                  ERROR this line not recovering previous indentation  
                """)
        self.assertEqual(err.exception.line.no, 4)         
                 

        with self.assertRaises(IndentError) as err:
            _parse("""
                if true
                    this line ok
                ERROR this line should be preceeded or followed by a blank line 
                this line ok
                """) 
        self.assertEqual(err.exception.line.no, 4)         


#---- Run module tests ----#

if __name__ == '__main__':
    unittest.main()  



