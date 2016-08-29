from collections import namedtuple

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
        self._text = self._text or self.source[self.pos:self.endpos]
        return self._text     

    @staticmethod
    def mock(source, no=1, pos=0):
        return Line(no, pos, source)    


         

