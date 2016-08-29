import unittest
from .line import *

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
