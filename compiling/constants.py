import llvmlite.ir as ir

F64 = ir.DoubleType()

I32 = ir.IntType(32)

LLVM_OPS = {

    # Floating point
    "fadd" : ( ir.IRBuilder.fadd, F64, F64, F64 ),
    "fmul" : ( ir.IRBuilder.fmul, F64, F64, F64 ),
    "fsub" : ( ir.IRBuilder.fsub, F64, F64, F64 ),
    "fdiv" : ( ir.IRBuilder.fdiv, F64, F64, F64 ),
    "frem" : ( ir.IRBuilder.frem, F64, F64, F64 ),

    # Integers
    "shl"  : ( ir.IRBuilder.shl, I32, I32, I32),
    "lshr"  : ( ir.IRBuilder.lshr, I32, I32, I32),
    "ashr"  : ( ir.IRBuilder.ashr, I32, I32, I32),
    "add"  : ( ir.IRBuilder.add, I32, I32, I32),
    "sub"  : ( ir.IRBuilder.sub, I32, I32, I32),
    "mul"  : ( ir.IRBuilder.mul, I32, I32, I32),
    "sdiv"  : ( ir.IRBuilder.sdiv, I32, I32, I32),
    "udiv"  : ( ir.IRBuilder.udiv, I32, I32, I32),
    "srem"  : ( ir.IRBuilder.srem, I32, I32, I32),
    "urem"  : ( ir.IRBuilder.urem, I32, I32, I32),
    "and"  : ( ir.IRBuilder.and_, I32, I32, I32),
    "or"  : ( ir.IRBuilder.or_, I32, I32, I32),
    "xor"  : ( ir.IRBuilder.xor, I32, I32, I32),
    "not"  : ( ir.IRBuilder.not_, I32, I32),
    "neg"  : ( ir.IRBuilder.neg, I32, I32),

    # Conversion
    "fptosi"  : ( lambda builder, val, name : 
        ir.IRBuilder.fptosi(builder, val, I32, name), I32, F64),
    
}