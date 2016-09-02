from collections import namedtuple
import re

from .semchecker import *

class IrResult(SeqMixin, namedtuple("_IrResult", "irval type seq calleeseq")):

    def __init__(self, irval, type, seq, calleeseq):
        pass


def _kcall_to_ir(kcall, builder):
    irargs = [arg.to_ir(builder).irval for arg in kcall.args]
    llvm_op = kcall.fun
    return IrResult(llvm_op.gen_fun(builder, *irargs, llvm_op.name),
        kcall.type, kcall.seq, kcall.calleeseq)        


def _kval_to_ir(kval, builder):
    return IrResult(kval.type(kval.val), kval.type, kval.seq, kval.seq)
    

setattr(KCall, 'to_ir', _kcall_to_ir)
setattr(KVal, 'to_ir', _kval_to_ir)


IrModuleResult = namedtuple("_IrModuleResult", "module type")

def ir_from(kcall):
    """ Generate an IR of the code in the call tree kcall.
        Returns a (module, return_type) with 
        a "main" function having that code.
    """
    # Create a module to insert the IR code in
    module = ir.Module()

    # Create a main(): double function
    funcname = "main"
    functype = ir.FunctionType(F64, [])
    func = ir.Function(module, functype, funcname)

    # Create the entry BB in the function and set a new builder to it.
    bb_entry = func.append_basic_block('entry')
    builder = ir.IRBuilder(bb_entry)    

    # Convert kcall to a F64 before returning from the fun
    f64call = check_type(kcall, F64)

    # Generate IR code 
    result = f64call.to_ir(builder)

    # And make the main function return that value
    builder.ret(result.irval)

    return IrModuleResult(module, kcall.type)




