from collections import namedtuple
from .source import Source

class Line(namedtuple('_Line', 'no pos source')):
    """
    Information about a line in sourcecode.
    Works in combination with char_feeder to assure proper instantiation.
    """

    def __init__(self, no, pos, source):
        # The following are unknown at initialization,
        # But will be set when known
        self.endpos = None
        self.indentpos = None
        self._text = None

    @property
    def len(self):
        "None if endpos is unknown."
        return self.endpos and self.endpos - self.pos        

    @property
    def indentsize(self):
        "None if indentpos is unknown."
        return self.indentpos and self.indentpos - self.pos        

    @property
    def text(self):
        "None if endpos is unkwnown."
        if self.endpos is None : return None
        # Cache result on the first time needed
        self._text = self._text or self.source.text[self.pos:self.endpos]
        return self._text     

    @staticmethod
    def mock(codestr, no=1, pos=0):
        return Line(no, pos, Source.mock(codestr))    

#---- Some unit tests ----#

import unittest

class TestLine(unittest.TestCase):

    def test_line(self):

        line = Line.mock("")
        self.assertEqual( line.len, None )
        self.assertEqual( line.text, None )
        self.assertEqual( line.indentsize, None )
        line.endpos = 0
        self.assertEqual( line.len, 0 )
        self.assertEqual( line.text, "" )
        line.indentpos = 0
        self.assertEqual( line.indentsize, 0 )

        line = Line.mock("  Allo!")
        line.endpos = 7
        self.assertEqual( line.len, 7 )
        self.assertEqual( line.text, "  Allo!" )
        line.indentpos = 2
        self.assertEqual( line.indentsize, 2 )

if __name__ == '__main__':
    unittest.main()            

