
from .source import Source
from .span import Span
from .line import Line


class CharFeederIsEmpty(Exception):
    pass

class BasicCharFeeder:

    def __init__(self, source):
        self.SOURCE = source
        self.CODE = source.text
        self.start = 0
        self.pos = -1
        self.current = None
        self.next()        

    def is_empty(self):
        return self.pos == self.SOURCE.len

    def next(self):
        if self.is_empty():
            raise CharFeederIsEmpty()

        self.pos += 1    

        if self.pos == self.SOURCE.len:
            self.current = ''
            return

        self.current = self.CODE[self.pos]

    def start_span(self):        
        self.start = self.pos

    def get_span(self):
        return Span(self.start, self.pos, self.SOURCE)


class CharFeeder (BasicCharFeeder):

    def __init__(self, source):
        BasicCharFeeder.__init__(self, source)
        self.lineno = 1
        self.linepos = 0

    def next(self):
        if self.current == '\n':
            self.lineno += 1
            self.linepos = self.pos + 1

        BasicCharFeeder.next(self)


    def get_line(self):
        return Line(self.lineno, self.linepos, self.SOURCE)             



#---- Some unit tests ----#

import unittest

class TestCharFeeder(unittest.TestCase):

    def test_empty(self):
        f = CharFeeder(Source.mock(""))
        self.assertTrue( f.is_empty() )
        self.assertEqual( f.current, "" )
        self.assertRaises(CharFeederIsEmpty, f.next)
        f.start_span()
        s = f.get_span()
        self.assertEqual(s, Span(0, 0, Source.mock("")))

    def _eat(self, f, char):    
        self.assertEqual( f.current, char )
        f.next()

    def test_nonempty(self):
        src = Source.mock("alpha")
        f = CharFeeder(src)
        self.assertFalse( f.is_empty() )
        self._eat( f, "a" )
        self._eat( f, "l" )
        f.start_span()
        self._eat( f, "p" )
        self._eat( f, "h" )
        s = f.get_span()
        self.assertEqual(s, Span(2, 4, src))
        self.assertEqual(s.text, 'ph')
        self._eat( f, "a" )
        self.assertEqual( f.current, "" )
        self.assertTrue( f.is_empty() )
        self.assertRaises(CharFeederIsEmpty, f.next)

    def test_multiline(self):
        src = Source.mock("1\n2\n3\n")
        f = CharFeeder(src)
        self.assertEqual(f.get_line(), Line(1,0,src))
        self._eat( f, "1" )
        self.assertEqual(f.get_line(), Line(1,0,src))
        self._eat( f, "\n" )
        self.assertEqual(f.get_line(), Line(2,2,src))
        self._eat( f, "2" )
        self._eat( f, "\n" )
        self._eat( f, "3" )
        self.assertEqual(f.get_line(), Line(3,4,src))
        self._eat( f, "\n" )
        self.assertEqual(f.get_line(), Line(4,6,src))

    def test_multiline_onlynewline(self):
        src = Source.mock("\n\n\n")
        f = CharFeeder(src)
        self.assertEqual(f.get_line(), Line(1,0,src))
        self._eat( f, "\n" )
        self.assertEqual(f.get_line(), Line(2,1,src))
        self._eat( f, "\n" )
        self.assertEqual(f.get_line(), Line(3,2,src))
        self._eat( f, "\n" )
        self.assertEqual(f.get_line(), Line(4,3,src))


if __name__ == '__main__':
    unittest.main()            