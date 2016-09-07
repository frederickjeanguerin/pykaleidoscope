from collections import namedtuple

from .types import *

LlvmOp = namedtuple('LlvmOp', 'name ret_type arg_types gen_fun')

_LLVM_OPS_DATA = {

    # Floating point
    "fadd" : ( F64, (F64, F64) , ir.IRBuilder.fadd),
    "fmul" : ( F64, (F64, F64) , ir.IRBuilder.fmul),
    "fsub" : ( F64, (F64, F64) , ir.IRBuilder.fsub),
    "fdiv" : ( F64, (F64, F64) , ir.IRBuilder.fdiv),
    "frem" : ( F64, (F64, F64) , ir.IRBuilder.frem),

    # Integers
    "shl"  : ( INT, (INT, INT) , ir.IRBuilder.shl),
    "lshr" : ( INT, (INT, INT) , ir.IRBuilder.lshr),
    "ashr" : ( INT, (INT, INT) , ir.IRBuilder.ashr),
    "add"  : ( INT, (INT, INT) , ir.IRBuilder.add),
    "sub"  : ( INT, (INT, INT) , ir.IRBuilder.sub),
    "mul"  : ( INT, (INT, INT) , ir.IRBuilder.mul),
    "sdiv" : ( INT, (INT, INT) , ir.IRBuilder.sdiv),
    "udiv" : ( INT, (INT, INT) , ir.IRBuilder.udiv),
    "srem" : ( INT, (INT, INT) , ir.IRBuilder.srem),
    "urem" : ( INT, (INT, INT) , ir.IRBuilder.urem),
    "and"  : ( INT, (INT, INT) , ir.IRBuilder.and_),
    "or"   : ( INT, (INT, INT) , ir.IRBuilder.or_),
    "xor"  : ( INT, (INT, INT) , ir.IRBuilder.xor),
    "not"  : ( INT, (INT,) , ir.IRBuilder.not_),
    "neg"  : ( INT, (INT,) , ir.IRBuilder.neg),

    # Conversion
    "fptosi" : ( INT, (F64,) , 
        lambda builder, val, name : 
            ir.IRBuilder.fptosi(builder, val, INT.irtype, name)),   
    "sitofp" : ( F64, (INT,) , 
        lambda builder, val, name : 
            ir.IRBuilder.sitofp(builder, val, F64.irtype, name)),   
}

def _init_llvm_ops(data):
    llvm_ops = dict()
    for key, value in data.items():
        llvm_ops[key] = LlvmOp('%' + key, *value)
    return llvm_ops    

LLVM_OPS = _init_llvm_ops(_LLVM_OPS_DATA)

