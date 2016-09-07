from collections import namedtuple
import re

from .semchecker import *


IrModuleResult = namedtuple("_IrModuleResult", "module type")

def ir_from(tree):
    """ Generate an IR of the code in the call tree.
        Returns a (module, return_type) with 
        a "main" function having that code.
    """
    # Create a module to insert the IR code in
    module = ir.Module()

    # Create a main(): double function
    funcname = "main"
    functype = ir.FunctionType(F64.irtype, [])
    func = ir.Function(module, functype, funcname)

    # Create the entry BB in the function and set a new builder to it.
    bb_entry = func.append_basic_block('entry')
    builder = ir.IRBuilder(bb_entry)    

    # Convert tree to a F64 before returning from the fun
    f64tree = check_type(tree, F64)

    # Generate IR code 
    result = f64tree.build_ir(builder)

    # And make the main function return that value
    builder.ret(result)

    return IrModuleResult(module, tree.type)




