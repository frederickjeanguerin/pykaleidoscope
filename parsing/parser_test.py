
from .parser import *
from pytest import raises

def _parse(codestr):
    return seq_from(next(stmts_from(tokens_from(codestr))))

def _assert(codestr):
    assert _parse(codestr).to_code() == "(" + codestr + ")"

def _error(codestr, colno):
    with raises(ParseError) as err:
        _parse(codestr)
    assert err.value.token.colno == colno        

def test_seq_simple():
    seq = _parse("0")
    assert seq.match(Seq)
    assert seq.items[0].match("0")
    assert seq.to_code() == "(0)"

def test_seq_complex():
    _assert("0 1 2")
    _assert("0 (1 2)")
    _assert("((0)) (1 2)")
    _assert("(()) (1 2)")
    
def test_errors():
    _error(")", 1)
    _error(" ( ", 2)
    _error("  ,", 3)
    _error("f()", 2)
    _error("()x", 3)
    _error("(x)(y)", 4)
    