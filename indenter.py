from collections import namedtuple
from lexing.lexer import tokens_from, Token, TokenKind, Source, Span
import pdb



class IndentError(Exception): 

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


class Stmt(namedtuple('_Stmt', 'tokblocks')):

    __slots__ = ()

    def __init__(self, tokblocks): 
        pass

    @property    
    def indent(self):
        return self.tokblocks[0].indent    

    def flatten(self):
        return [tb.text if isinstance(tb, Token) else tb.flatten() for tb in self.tokblocks]        


class IndenterFeeder :

    def __init__(self, tokens_gen):
        self._tokens = tokens_gen
        self.previous = None
        self.current = next(self._tokens)

    def fetch(self):    
        """Fetch the next token from the token source."""    
        self.previous = self.current
        if not self.previous.eof:    
            self.current = next(self._tokens)

    @property
    def line_gap(self):
        """ Line gap between current and previous token
            0 if both are on the same line
            1 if current on the next line
            2 if there is a blank line in between, etc.
        """
        return self.current.linein - self.previous.linein        


def _parseBlock(feeder):
    assert not feeder.current.eof
    stmts = list()
    indent = feeder.current.indent 
    while feeder.current.indent == indent:
        stmts.append(_parseStmt(feeder))
    return Block(stmts)    

def _parseLine(feeder, tokblocks):
    # A line has at least one token
    assert not feeder.current.eof

    # Eat up the line
    linein = feeder.current.linein
    while feeder.current.linein == linein :
        tokblocks.append(feeder.current)
        feeder.fetch()


def _parseStmt(feeder):
    tokblocks = []
    indent = feeder.current.indent
    _parseLine(feeder, tokblocks)
    indent_shift = feeder.current.indent - indent
    # While there is indentation 
    while indent_shift > 0:  
        if indent_shift == 1 :
            raise IndentError(feeder.current.line, "Indentation must be greater than 1 space")
        elif indent_shift > 4 :
            raise IndentError(feeder.current.line, "Indentation must be no more than 4 spaces")
        # Parse the block    
        tokblocks.append(_parseBlock(feeder))

        # Check indentation after the block        
        indent_shift = feeder.current.indent - indent
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
        indent_shift = feeder.current.indent - indent
        # If there is an unindent or if there is a blank line, end statement
        if indent_shift < 0 or (indent_shift == 0 and feeder.line_gap >= 2):
            break
        # If there is another line, then error
        if indent_shift == 0:
            raise IndentError(feeder.current.line, "There should be a blank line before this one or the previous one, or this line should be indented or outdented.")
        # Otherwise, there is a new indentation, so just loop
        assert indent_shift > 0    
        
    return Stmt(tokblocks)        
        

def all_stmts_from(tokens_gen):
    feeder = IndenterFeeder(tokens_gen)
    if feeder.current.eof:
        return Block([])
    # TODO warn if initial indent_level > 0
    block = _parseBlock(feeder)
    if not feeder.current.eof:
        raise IndentError(feeder.current.line)
    return block   



import unittest


def _parse(codestr):
    return all_stmts_from(tokens_from(Source.mock(codestr)))

class TestIndenter(unittest.TestCase):

    def __assert(self, codestr, flattened):
        block = _parse(codestr)
        self.assertListEqual(block.flatten(), flattened)

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

    def test_indent_error(self):

        with self.assertRaises(IndentError):
            _parse("""
                if true
                 this line not indented enough
                """) 

        with self.assertRaises(IndentError):
            _parse("""
                if true
                            this line indented too much
                """) 

        with self.assertRaises(IndentError):
            _parse("""
                if true
            this line outdented
                """) 

        with self.assertRaises(IndentError):
            _parse("""
                if true
                    this line ok
                  this line not recovering previous indentation  
                """) 

        with self.assertRaises(IndentError):
            _parse("""
                if true
                    this line ok
                this line ok
                this line should be preceeded by a blank line   
                """) 


#---- Run module tests ----#

if __name__ == '__main__':
    unittest.main()  

    # codestr="""
    #         if true
    #           be foolish
    #         else
    #           be sad  
    #         """        

    # block = all_stmts_from(tokens_from(Source.mock(codestr)))
    # print(block.flatten())

