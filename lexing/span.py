from .mixin import *

class Span(EqualityMixin, StrMixin):
    """ Describe a span of text in source code:
            start : starting offset from beginning starting at 0
            stop  : stopping offset + 1
    """
    def __init__(self, start, stop, source):
        self.start = start
        self.stop = stop
        self.source = source
        self._text = None

    @property 
    def len(self):
        return self.stop - self.start

    @property    
    def text(self):
        """ Returns the span text

            NB Slices in Python return string copies, 
            which is expensive, so we cache the result
        """    
        if not self._text:
            self._text = self.source.text[self.start:self.stop]    
        return self._text

def mock(codestr = "mocked_span_codestr"):    
    return Span(0, len(codestr), source.mock(codestr))


#---- Some unit tests ----#

import unittest
from . import source

class TestSource(unittest.TestCase):

    def test_equality(self):
        self.assertEqual( mock(), mock() )

    def test_text(self):
        span = Span(2, 4, source.Source("test", "012345" ))
        self.assertEqual( span.text, "23" )

if __name__ == '__main__':
    unittest.main()            