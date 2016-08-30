from .parser_feeder import *

def test_feeder():

    f = ParserFeeder(indent("if a <b:").stmts[0])

    assert f.match("if")
    assert f.match(Identifier)
    assert f.is_unglued
    assert f.eat("if").text == "if"

    assert f.match('a')
    assert f.is_unglued
    f.eat('a')

    assert f.match('<')
    assert f.is_right_glued
    f.eat('<')

    assert f.match('b')
    assert f.is_glued
    f.eat('b')

    assert f.match(':')
    assert f.is_left_glued
    f.eat(':')

    assert f.match(None)
    