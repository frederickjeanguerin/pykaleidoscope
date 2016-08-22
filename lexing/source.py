from collections import namedtuple


class Source (namedtuple('_Source', 'name text')) :
    """ Source code descriptor : immutable 
            name : the name, filename or origin of the Source 
            text : the entire string content of the source
    """

    # The following makes it impossible to add new attributes to the object
    __slots__ = ()

    @property
    def len(self):
        return len(self.text)

    @staticmethod    
    def mock(codestr = "mocked_source_codestr"):
        return Source('mocked_name', codestr)


#---- Some unit tests ----#

import unittest

class TestSource(unittest.TestCase):



    def test_no_dict(self):
        with self.assertRaises(AttributeError):
            Source.mock().xxx = 90

    def test_source(self):
        s1 = Source.mock("A")
        s2 = Source.mock("A")
        self.assertEqual(s1.text, "A")
        self.assertEqual(s1.name, s2.name)
        self.assertEqual(s1.len, 1)
        self.assertEqual(s1, s2)

    def test_equality(self):
        self.assertEqual( Source.mock(), Source.mock() )


if __name__ == '__main__':
    unittest.main()            