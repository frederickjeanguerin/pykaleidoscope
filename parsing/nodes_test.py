
from .nodes import *

def test_seq():
    seq = Seq([], Token.mock("("), Token.mock(")"))
    assert seq.flatten() == []
    assert seq.first_token.text == "(" 
    assert seq.last_token.text == ")" 

    seq = Seq([Token.mock("A"), Token.mock("B"), Token.mock("C")])
    assert seq.flatten() == ["A", "B", "C"]
    assert seq.first_token.text == "A" 
    assert seq.last_token.text == "C" 

def test_call():
    call = Call( Token.mock("f"), [], Token.mock("("), Token.mock(")") )
    assert call.flatten() == ['Call', 'f', []]
    assert call.first_token.text == "(" 
    assert call.last_token.text == ")" 

    call = Call( Token.mock("f"), [Token.mock("x"), Token.mock("y")], Token.mock("("), Token.mock(")") )
    assert call.flatten() == ['Call', 'f', ['x', 'y']]

