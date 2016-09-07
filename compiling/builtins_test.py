from .builtins import *

def test_builtins():

    add, alternatives = SYMTAB.find("add", INT, INT)
    fadd, alternatives = SYMTAB.find("add", F64, F64)
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

    assert SYMTAB.find("add", INT, INT)[0] == None
    assert SYMTAB.find("add", F64, F64)[0] == None

    SYMTAB.add(add)
    SYMTAB.add(fadd)
    
    assert SYMTAB.find("add", INT, INT)[0] == add
    assert SYMTAB.find("add", F64, F64)[0] == fadd

    
    