from .types import *

def test_types():
    assert INT == INT
    assert INT.irtype == ir.IntType(INT_SIZE)
    assert INT.irtype is ir.IntType(INT_SIZE)

    