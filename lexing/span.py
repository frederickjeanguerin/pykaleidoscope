from collections import namedtuple
from .source import Source

class Span(namedtuple('_Span', 'start stop source')):
    """ Span of text in source code: immutable
            start : starting offset from beginning starting at 0
            stop  : stopping offset + 1
    """

    def __init__(self, start, stop, source):
        # There is no need to initialise the fields 
        # because the namedtuple ancestor took car of it
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
        self._text = self._text or self.source.text[self.start:self.stop]    
        return self._text

    @staticmethod    
    def mock(codestr = "mocked_span_codestr"):    
        return Span(0, len(codestr), Source.mock(codestr))


#---- Some unit tests ----#

import unittest

class __TestSpan(unittest.TestCase):

    def test_equality(self):
        self.assertEqual( Span.mock(), Span.mock() )

    def test_text(self):
        
        span1 = Span(2, 4, Source("test", "012345" ))
        span2 = Span(2, 4, Source("test", "012345" ))
        self.assertEqual( span1, span2 )
        self.assertEqual( span1.text, "23" )
        self.assertEqual( span1, span2 )

if __name__ == '__main__':
    unittest.main()
