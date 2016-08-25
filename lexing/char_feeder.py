
from .line import Line

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


class CharFeeder (BasicCharFeeder):

    def __init__(self, source):
        self.lineno = 1
        self.line = Line(self.lineno, 0, source)
        super().__init__(source)

    def next(self):
        """
        Advance the feeder to the next available char.

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




#---- Some unit tests ----#

import unittest

class TestCharFeeder(unittest.TestCase):

    def test_empty(self):
        f = CharFeeder("")
        self.assertTrue( f.is_empty() )
        self.assertEqual( f.current, '' )
        self.assertRaises(CharFeederIsEmpty, f.next)

    def _eat(self, f, string):
        for char in string:    
            self.assertEqual( f.current, char )
            f.next()

    def test_nonempty(self):
        f = CharFeeder("alpha")
        self.assertFalse( f.is_empty() )
        self._eat( f, "alpha" )
        self.assertEqual( f.current, '' )
        self.assertTrue( f.is_empty() )
        self.assertRaises(CharFeederIsEmpty, f.next)

    def test_multiline(self):
        src = "1\n2\n3\n"
        f = CharFeeder(src)
        self.assertEqual(f.line, Line(1,0,src))
        self._eat( f, "1" )
        self.assertEqual(f.line, Line(1,0,src))
        self._eat( f, "\n" )
        self.assertEqual(f.line, Line(2,2,src))
        self._eat( f, "2\n3" )
        self.assertEqual(f.line, Line(3,4,src))
        self._eat( f, "\n" )
        self.assertEqual(f.line, Line(4,6,src))

    def test_multiline_onlynewline(self):
        src = "\n\n\n"
        f = CharFeeder(src)
        self.assertEqual(f.line, Line(1,0,src))
        self._eat( f, "\n" )
        self.assertEqual(f.line, Line(2,1,src))
        self._eat( f, "\n" )
        self.assertEqual(f.line, Line(3,2,src))
        self._eat( f, "\n" )
        self.assertEqual(f.line, Line(4,3,src))

    def test_line_text(self):
        src = "\n allo \n yo "
        f = CharFeeder(src)

        line1 = f.line
        self.assertEqual(line1.text, None)
        self._eat( f, "\n")
        line2 = f.line
        self._eat( f, "allo " )
        self.assertEqual(line2.text, None)
        self._eat( f, "\n" )
        line3 = f.line
        self._eat( f, "yo " )

        self.assertEqual(line1.text, "\n")
        self.assertEqual(line2.text, " allo \n")
        self.assertEqual(line3.text, " yo ")
        
    def test_line_indentation(self):
        src = "     \n  allo \n   \n"
        f = CharFeeder(src)

        self.assertEqual(f.line.indentsize, 5)
        self._eat( f, "\n")

        line2 = f.line
        self._eat( f, "allo \n")
        line3 = f.line
        self._eat( f, "\n")

        self.assertEqual(line2.indentsize, 2)
        self.assertEqual(line3.indentsize, 3)

        

if __name__ == '__main__':
    unittest.main()            