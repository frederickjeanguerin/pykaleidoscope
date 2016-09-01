import llvmlite.ir as ir

F64 = ir.DoubleType()

INT_SIZE = 32

INT = ir.IntType(INT_SIZE)

LLVM_OPS = {

    # Floating point
    "fadd" : ( ir.IRBuilder.fadd, F64, F64, F64 ),
    "fmul" : ( ir.IRBuilder.fmul, F64, F64, F64 ),
    "fsub" : ( ir.IRBuilder.fsub, F64, F64, F64 ),
    "fdiv" : ( ir.IRBuilder.fdiv, F64, F64, F64 ),
    "frem" : ( ir.IRBuilder.frem, F64, F64, F64 ),

    # Integers
    "shl"  : ( ir.IRBuilder.shl, INT, INT, INT),
    "lshr"  : ( ir.IRBuilder.lshr, INT, INT, INT),
    "ashr"  : ( ir.IRBuilder.ashr, INT, INT, INT),
    "add"  : ( ir.IRBuilder.add, INT, INT, INT),
    "sub"  : ( ir.IRBuilder.sub, INT, INT, INT),
    "mul"  : ( ir.IRBuilder.mul, INT, INT, INT),
    "sdiv"  : ( ir.IRBuilder.sdiv, INT, INT, INT),
    "udiv"  : ( ir.IRBuilder.udiv, INT, INT, INT),
    "srem"  : ( ir.IRBuilder.srem, INT, INT, INT),
    "urem"  : ( ir.IRBuilder.urem, INT, INT, INT),
    "and"  : ( ir.IRBuilder.and_, INT, INT, INT),
    "or"  : ( ir.IRBuilder.or_, INT, INT, INT),
    "xor"  : ( ir.IRBuilder.xor, INT, INT, INT),
    "not"  : ( ir.IRBuilder.not_, INT, INT),
    "neg"  : ( ir.IRBuilder.neg, INT, INT),

    # Conversion
    "fptosi"  : ( lambda builder, val, name : 
        ir.IRBuilder.fptosi(builder, val, INT, name), INT, F64),
    
}