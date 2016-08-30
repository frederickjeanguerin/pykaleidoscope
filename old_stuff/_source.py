class Source (str) :
    """ 
        Source code descriptor

        Behaves like a string but can can receive an additionnal field, 
        an `origin` that says where the source comes from.
    """

    __slots__ = ("origin")

    def __new__(cls, codestr, origin = None):
        self = super(Source,cls).__new__(cls, codestr)
        self.origin = origin
        return self

    @property
    def text(self):
        return self

    @property
    def len(self):
        return len(self)


#---- Some unit tests ----#

import unittest

class TestSource(unittest.TestCase):


    def test_source(self):
        s = Source("Alpha")
        self.assertEqual(s, "Alpha")
        self.assertEqual(s.text, "Alpha")
        self.assertEqual(s.len, 5)
        self.assertTrue(isinstance(s, str))
        self.assertEqual(s.origin, None)
        s.origin = "File"
        self.assertEqual(s.origin, "File")
        s = Source("Alpha", "Beta")
        self.assertEqual(s.origin, "Beta")
        


if __name__ == '__main__':
    unittest.main()            