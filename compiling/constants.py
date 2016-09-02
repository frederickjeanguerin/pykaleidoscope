from collections import namedtuple 
import llvmlite.ir as ir

F64 = ir.DoubleType()

INT_SIZE = 32

INT = ir.IntType(INT_SIZE)

LlvmOp = namedtuple('LlvmOp', 'ret_type arg_types gen_fun')

LLVM_OPS = {

    # Floating point
    "fadd" : LlvmOp( F64, (F64, F64) , ir.IRBuilder.fadd),
    "fmul" : LlvmOp( F64, (F64, F64) , ir.IRBuilder.fmul),
    "fsub" : LlvmOp( F64, (F64, F64) , ir.IRBuilder.fsub),
    "fdiv" : LlvmOp( F64, (F64, F64) , ir.IRBuilder.fdiv),
    "frem" : LlvmOp( F64, (F64, F64) , ir.IRBuilder.frem),

    # Integers
    "shl"  : LlvmOp( INT, (INT, INT) , ir.IRBuilder.shl),
    "lshr" : LlvmOp( INT, (INT, INT) , ir.IRBuilder.lshr),
    "ashr" : LlvmOp( INT, (INT, INT) , ir.IRBuilder.ashr),
    "add"  : LlvmOp( INT, (INT, INT) , ir.IRBuilder.add),
    "sub"  : LlvmOp( INT, (INT, INT) , ir.IRBuilder.sub),
    "mul"  : LlvmOp( INT, (INT, INT) , ir.IRBuilder.mul),
    "sdiv" : LlvmOp( INT, (INT, INT) , ir.IRBuilder.sdiv),
    "udiv" : LlvmOp( INT, (INT, INT) , ir.IRBuilder.udiv),
    "srem" : LlvmOp( INT, (INT, INT) , ir.IRBuilder.srem),
    "urem" : LlvmOp( INT, (INT, INT) , ir.IRBuilder.urem),
    "and"  : LlvmOp( INT, (INT, INT) , ir.IRBuilder.and_),
    "or"   : LlvmOp( INT, (INT, INT) , ir.IRBuilder.or_),
    "xor"  : LlvmOp( INT, (INT, INT) , ir.IRBuilder.xor),
    "not"  : LlvmOp( INT, (INT,) , ir.IRBuilder.not_),
    "neg"  : LlvmOp( INT, (INT,) , ir.IRBuilder.neg),

    # Conversion
    "fptosi" : LlvmOp( INT, (F64,) , 
        lambda builder, val, name : 
            ir.IRBuilder.fptosi(builder, val, INT, name)),   
}