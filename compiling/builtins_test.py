from .builtins import *

def test_builtins():

    add, alternatives = SYMTAB.find("add", (INT, INT))
    fadd, alternatives = SYMTAB.find("add", (F64, F64))
    assert add.llvmop_name == "add"
    assert fadd.llvmop_name == "fadd"
    sym, alternatives = SYMTAB.find("!@#$%")
    assert sym == alternatives == None
    sym, alternatives = SYMTAB.find("add")
    assert sym == None
    assert add in alternatives and fadd in alternatives

    # import pdb
    # pdb.set_trace()

    SYMTAB.remove(add)
    SYMTAB.remove(fadd)

    assert SYMTAB.find("add", (INT, INT))[0] == None
    assert SYMTAB.find("add", (F64, F64))[0] == None

    SYMTAB.add(add)
    SYMTAB.add(fadd)
    
    assert SYMTAB.find("add", (INT, INT))[0] == add
    assert SYMTAB.find("add", (F64, F64))[0] == fadd


def test_aliases():

    sym1, alternatives = SYMTAB.find("i32", (F64,), ALIASES)
    sym2, alternatives = SYMTAB.find("int", (F64,), ALIASES)
    assert sym1 == sym2
    
def test_distance():
    assert SYMTAB.distance((INT,INT), (INT, INT)) == 0
    assert SYMTAB.distance((INT,INT), (F64, F64)) == TOO_FAR
    assert SYMTAB.distance((INT,INT), (F64, F64), AUTOMATIC_PROMOTIONS) == 2
    assert SYMTAB.distance((INT,F64), (F64, F64), AUTOMATIC_PROMOTIONS) == 1
    
def test_find_with_promotion():

    add, alternatives = SYMTAB.find("add", (INT, INT))
    fadd, alternatives = SYMTAB.find("add", (F64, F64))
    fadd1, alternatives = SYMTAB.find("add", (INT, F64), ALIASES, AUTOMATIC_PROMOTIONS)
    fadd2, alternatives = SYMTAB.find("add", (F64, INT), ALIASES, AUTOMATIC_PROMOTIONS)
    assert add != fadd
    assert fadd1 == fadd
    assert fadd2 == fadd


    