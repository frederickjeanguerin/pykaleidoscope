from derivedtuple import derivedtuple
from .source import Source

class LineMixin:

    @property
    def endpos(self):
        """ Offset in source of the end of the line, including \n """

        pos = self.pos
        code = self.source.text
        codelen = self.source.len

        while pos < codelen :
            if code[pos] == '\n':
                return pos + 1
            pos += 1
        return pos

    @property
    def len(self):
        return self.endpos - self.pos        

    @property
    def text(self):
        return self.source.text[self.pos:self.endpos]        

    @staticmethod
    def mock(codestr, no=1, pos=0):
        return Line(no, pos, Source.mock(codestr))    

Line = derivedtuple("Line", "no pos source", LineMixin)


#---- Some unit tests ----#

import unittest

class TestLine(unittest.TestCase):

    def test_line(self):

        line = Line.mock("")
        self.assertEqual( line.endpos, 0 )
        self.assertEqual( line.len, 0 )
        self.assertEqual( line.text, "" )

        line = Line.mock("\n")
        self.assertEqual( line.endpos, 1 )
        self.assertEqual( line.len, 1 )
        self.assertEqual( line.text, "\n" )

        line = Line.mock("Allo!")
        self.assertEqual( line.endpos, 5 )
        self.assertEqual( line.len, 5 )
        self.assertEqual( line.text, "Allo!" )

        line = Line.mock("Allo!\n")
        self.assertEqual( line.endpos, 6 )
        self.assertEqual( line.len, 6 )
        self.assertEqual( line.text, "Allo!\n" )

        line = Line.mock("Bonjour\nles amis!")
        self.assertEqual( line.endpos, 8 )
        self.assertEqual( line.len, 8 )
        self.assertEqual( line.text, "Bonjour\n" )

        line = Line.mock("Bonjour\nles amis!", 2, 8)
        self.assertEqual( line.endpos, 17 )
        self.assertEqual( line.len, 9 )
        self.assertEqual( line.text, "les amis!" )


if __name__ == '__main__':
    unittest.main()            

