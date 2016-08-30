
from .seq import *

def test_seq():
    seq = Seq([], Token.mock("("), Token.mock(")"))
    assert seq.to_code() == "()"
    assert seq.first_token.text == "(" 
    assert seq.last_token.text == ")" 

    seq2 = Seq([Token.mock("A"), Token.mock("B"), Token.mock("C")])
    assert seq2.to_code() == "(A B C)"
    assert seq2.first_token.text == "A" 
    assert seq2.last_token.text == "C" 

    seq3 = Seq([Token.mock("A"), seq2])
    assert seq3.to_code() == "(A (A B C))"
    assert seq3.first_token.text == "A" 
    assert seq3.last_token.text == "C" 
