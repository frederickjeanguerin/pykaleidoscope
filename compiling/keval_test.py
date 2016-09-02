
from pytest import raises
from .keval import *

def _error(codestr, colno):
    with raises(SemanticError) as err:
        eval(codestr)
    assert err.value.target.colno == colno    

def test_eval():

    assert eval("0") == 0
    assert eval("90") == 90
    assert eval("0.99") == 0.99
    assert eval("%fadd 1 2") == 3
    assert eval("%fadd (%fadd 1 2) (%fadd 3 (%fadd 4 5))") == 15

def test_evals_gen():

    assert list(evals_gen("1\n2")) == [1,2]


def test_floating_arithmetics():

    assert eval("%fadd 2 1.5") == 3.5
    assert eval("%fmul 3 1.5") == 4.5
    assert eval("%fsub 4 1.5") == 2.5
    assert eval("%fdiv 5 2.5") == 2.0
    assert eval("%frem 6 2.5") == 1.0


def test_integer_arithmetics():

    assert eval("%add 2 1") == 3
    assert eval("%mul 3 2") == 6
    assert eval("%sub 4 3") == 1
    assert eval("%sdiv 15 6") == 2
    assert eval("%udiv 15 6") == 2
    assert eval("%srem 15 6") == 3
    assert eval("%urem 15 6") == 3
    assert eval("%neg 15") == -15

    # bitwise
    assert eval("%and 14 3") == 2
    assert eval("%or 14 3") == 15
    assert eval("%xor 14 3") == 13
    assert eval("%not 1") == -2

    # shift
    assert eval("%shl 8 2") == 32
    assert eval("%ashr 64 2") == 16
    assert eval("%lshr 64 2") == 16
    
def test_conversion():
    # automatic conversion from int to float
    assert eval("%fadd 1 2") == 3
    # not automatic from float to int
    _error("%add 1.0 2.0", 6)
    assert eval("%add (%fptosi 1.0) 2") == 3    

    
