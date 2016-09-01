from .constants import *

def test_types():
    assert INT == INT
    assert INT == ir.IntType(INT_SIZE)
    assert INT is ir.IntType(INT_SIZE)