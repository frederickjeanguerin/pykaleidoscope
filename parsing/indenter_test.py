
from .indenter import *
import unittest


class TestIndenter(unittest.TestCase):

    def __assert(self, codestr, flattened):
        block = indent(codestr)
        self.assertListEqual(block.flatten(), flattened)

    def __assert_dump(self, codestr, dumped = None):
        dumped = dumped or codestr
        block = indent(codestr)
        self.assertEqual(block.dump(4).strip(), dumped.strip())

    def __assert_many_dumps(self, *many_codestr):
        for codestr in many_codestr:
            self.__assert_dump(codestr)

    def test_unindented(self):
        self.__assert("", [])
        self.__assert("1", [['1']])
        self.__assert("1 2", [['1', '2']])
        self.__assert("1 2\n3 4", [['1', '2'],['3', '4']])
        self.__assert("1 2\n  \n3 4  \n", [['1', '2'],['3', '4']])

    def test_match(self):
        block = indent('a')
        self.assertTrue(block.match(Block))
        self.assertFalse(block.match(Stmt))
        self.assertTrue(block.stmts[0].match(Stmt)) 
        self.assertFalse(block.stmts[0].match(Block)) 

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
            indent("""
                if true
                 ERROR this line not indented enough
                """)
        self.assertEqual(err.exception.line.no, 3)         
        self.assertEqual(err.exception.refline.no, 2)         


        with self.assertRaises(IndentError) as err:
            indent("""
                if true
                      ERROR this line indented too much
                """)
        self.assertEqual(err.exception.line.no, 3)         
        self.assertEqual(err.exception.refline.no, 2)         
                 

        with self.assertRaises(IndentError) as err:
            indent("""
                if true
            ERROR this line outdented
                """) 
        self.assertEqual(err.exception.line.no, 3)         
        self.assertEqual(err.exception.refline.no, 2)         


        with self.assertRaises(IndentError) as err:
            indent("""
                if true
                    this line ok
                  ERROR this line not recovering previous indentation  
                """)
        self.assertEqual(err.exception.line.no, 4)         
        self.assertEqual(err.exception.refline.no, 2)         
                 

        with self.assertRaises(IndentError) as err:
            indent("""
                if true
                    this line ok
                ERROR this line should be preceeded or followed by a blank line 
                this line ok
                """) 
        self.assertEqual(err.exception.line.no, 4)         
        self.assertEqual(err.exception.refline.no, 2)         


    def test_line_continuation(self):

        self.__assert("""
            if true
                    be foolish
            """, 
            [
                ['if', 'true', 'be', 'foolish']   
            ])

        self.__assert("""
            if true
                    
                    be 
                    
                    foolish
            """, 
            [
                ['if', 'true', 'be', 'foolish']   
            ])

        self.__assert("""
            if true
                    be foolish
                    and
                    cool
                but beware

            else
              be sad  
            """, 
            [
                ['if', 'true', 'be', 'foolish', 'and', 'cool',
                    [['but', 'beware']]],
                ['else',
                    [['be', 'sad']]]   
            ])

        self.__assert("""
            if true
                    be foolish
                    and
                    cool
                but beware
            else
              be sad  
            """, 
            [
                ['if', 'true', 'be', 'foolish', 'and', 'cool',
                    [['but', 'beware']],
                'else',
                    [['be', 'sad']]]   
            ])


