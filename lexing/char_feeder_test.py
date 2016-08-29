
import unittest
from .char_feeder import *

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

    def test_new_token(self):
        f = CharFeeder(" allo\n")
        f.start_token()
        self._eat( f, "allo" )
        token = f.new_token(Identifier)
        self.assertEqual(token.text, "allo")
        self.assertEqual(token.lineno, 1)
        
