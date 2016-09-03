
from .ktree import *
from .llvm_ops import *
from .symtab import *

class BasicOp (namedtuple("_BasicOp", "name ret_type arg_types llvmop_name")):

    def __init__(self, name, ret_type, arg_types, llvmop_name):
        pass

    def make_call(self, treeargs, seq, cseq):
        return KCall(LLVM[self.llvmop_name], treeargs, self.ret_type, seq, cseq)

    def __repr__(self):
        return "{}({}):{} = {}".format(self.name, ",".join((str(typ) for typ in self.arg_types)), str(self.ret_type), self.llvmop_name )        

_BASICOP_DATA = [
    ("add", INT, (INT, INT), "add"), 
    ("add", F64, (F64, F64), "fadd"),
]


def _add_basic_ops(symtab, data):
    for datum in data:
        symtab.add(BasicOp(*datum)) 

_add_basic_ops(SYMTAB, _BASICOP_DATA)