
from pytest import raises
from .keval import *

def _error(codestr, colno):
    with raises(CodegenError) as err:
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


def test_error():

    _error("a", 1)
    _error("0.0.0", 1)
    _error("()", 1)
    _error("0 0", 1)
    _error("a 0", 1)
    _error("a 0 0", 1)
    _error("%fx 0 0", 1)
    _error("%fadd 0", 1)
    _error("%fadd", 1)
    _error("%fadd 0 1 2", 1)
    
