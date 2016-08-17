from mixin import *

class Source (EqualityMixin, StrMixin):
    """ Source code descriptor : immutable """

    def __init__(self, name, text):
        self.name = name
        self.text = text

    @property
    def len(self):
        return len(self.text)    


def mock(codestr = "mocked_source_codestr"):
    return Source('mocked_name', codestr)


#---- Some unit tests ----#

import unittest

class TestSource(unittest.TestCase):

    def test_equality(self):
        self.assertEqual( mock(), mock() )


if __name__ == '__main__':
    unittest.main()            