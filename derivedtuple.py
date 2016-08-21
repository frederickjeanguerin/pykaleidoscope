from collections import namedtuple

def derivedtuple(typename, properties, *parents):
    """Create a new namedtuple with ancestors in parents."""
    nt = namedtuple(typename, properties)
    # Add parents
    nt.__bases__ = tuple(parents) + nt.__bases__
    # Add method Flatten
    # setattr(nt, 'flatten', _flatten)
    return nt

#---- Some unit tests ----#

import unittest

class _PointMixin:

    @property
    def sum(self):
        return self.x + self.y


class TestDerivedTuple(unittest.TestCase):

    def test_underivedtuple(self):
        Point = derivedtuple('Point', 'x y')

        p = Point(8, 1)
        q = Point(8, 1)
        self.assertEqual( p, q )



    def test_derivedtuple(self):
        Point = derivedtuple('Point', 'x y', _PointMixin)

        p = Point(8, 1)
        q = Point(8, 1)
        self.assertEqual( p, q )
        self.assertEqual( p.sum, 9 )

if __name__ == '__main__':
    unittest.main()            

