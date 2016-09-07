from pytest import raises
from .semchecker import *


def _error(codestr, colno):
    with raises(SemanticError) as err:
        check_code(codestr)
    assert err.value.target.colno == colno    


def _assert(codestr, expected_code = None):
    expected_code = expected_code or codestr
    call_tree = check_expr(codestr)
    if call_tree.match(KCall):
        expected_code = '(' + expected_code + ')'
    assert check_expr(codestr).to_code() == expected_code


def test_chk_number():

    _assert("0")
    _assert("90")
    _assert("0.0")
    _assert("0.99")


def test_call_llvm_op():


    _assert("%fadd 1.0 2.0")
    _assert("%fadd (%fadd 1.0 2.0) (%fadd 3.0 (%fadd 4.0 5.0))")


def test_kcall_mixin():

    kval = check_expr(" 199 ")
    assert kval.pos == 1
    assert kval.endpos == 4

    kcall = check_expr(" %fadd 1.0 2.0 ")
    assert kcall.text == "%fadd 1.0 2.0"
    assert kcall.calleeseq.text == "%fadd"


def test_conversion():
    # automatic conversion from int to float
    _assert("%fadd 1 2", "%fadd (%sitofp 1) (%sitofp 2)" )


def test_basicop():
    _assert("add 1 2", "%add 1 2")
    _assert("add 1.1 2.2", "%fadd 1.1 2.2")

def test_identity_passthrough():
    _assert("i32 1", "1")
    _assert("i32 1.1", "%fptosi 1.1")
    _assert("f64 1.1", "1.1")
    _assert("f64 1", "%sitofp 1")

def test_error():

    _error("a", 1)
    _error("0.0.0", 1)
    _error("()", 1)
    _error("(2)", 2)
    _error("0 0", 1)
    _error("a 0", 1)
    _error("a 0 0", 1)
    _error("%fx 0 0", 1)
    _error("%fadd 0.0", 1)
    _error("%fadd", 1)
    _error("%fadd 0.0 1.0 2.0", 1)
    _error("%add 1.0 2.0", 6)

