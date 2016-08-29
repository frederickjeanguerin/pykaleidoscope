
import unittest
from derivedtuple import *

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


    def test_extensiontuple(self):
        Point = derivedtuple('Point', 'x y', _PointMixin)
        Point3D = derivedtuple('Point3D', 'x y z', Point)

        p = Point3D(1, 2, 3)
        self.assertEqual( p.sum, 3 )
        self.assertTrue( isinstance(p, _PointMixin) )
        

