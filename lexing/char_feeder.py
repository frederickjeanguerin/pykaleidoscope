from . import source
from .span import Span


class CharFeederIsEmpty(Exception):
    pass

class CharFeeder:

    def __init__(self, source):
        self.SOURCE = source
        self.CODE = source.text
        self.start = 0
        self.pos = -1
        self.next()

    def is_empty(self):
        return self.pos == self.SOURCE.len

    def next(self):
        if self.is_empty():
            raise CharFeederIsEmpty()

        self.pos += 1

        if self.pos == self.SOURCE.len:
            self.current = ''
        else:
            self.current = self.CODE[self.pos]

    def start_span(self):        
        self.start = self.pos

    def stop_span(self):
        return Span(self.start, self.pos, self.SOURCE)


#---- Some unit tests ----#

import unittest

class TestCharFeeder(unittest.TestCase):

    def test_empty(self):
        f = CharFeeder(source.mock(""))
        self.assertTrue( f.is_empty() )
        self.assertEqual( f.current, "" )
        self.assertRaises(CharFeederIsEmpty, f.next)
        f.start_span()
        s = f.stop_span()
        self.assertEqual(s, Span(0, 0, source.mock("")))

    def test_nonempty(self):
        src = source.mock("alpha")
        f = CharFeeder(src)
        self.assertFalse( f.is_empty() )
        self.assertEqual( f.current, "a" )
        f.next()
        self.assertEqual( f.current, "l" )
        f.next()
        self.assertEqual( f.current, "p" )
        f.start_span()
        f.next()
        f.next()
        s = f.stop_span()
        self.assertEqual(s, Span(2, 4, src))
        self.assertEqual(s.text, 'ph')
        f.next()
        self.assertEqual( f.current, "" )
        self.assertTrue( f.is_empty() )
        self.assertRaises(CharFeederIsEmpty, f.next)

if __name__ == '__main__':
    unittest.main()            