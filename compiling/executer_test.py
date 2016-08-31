from .executer import exec
from .optimizer import optimize
from .ircoder import *
from parsing.parser import *
from pytest import raises

def eval(codestr):
    return exec(optimize(ir_from(parse(codestr))))    

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

def test_error():

    _error("a", 1)
    _error("()", 1)
    _error("0 0", 1)
    _error("a 0", 1)
    _error("a 0 0", 1)
    _error("%fx 0 0", 1)
    _error("%fadd 0", 1)
    _error("%fadd", 1)
    _error("%fadd 0 1 2", 1)
    
