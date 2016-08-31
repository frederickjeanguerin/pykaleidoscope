from ctypes import CFUNCTYPE, c_double
import llvmlite.binding as llvm

# All these initializations are required for code generation!
llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()  # yes, even this one

# Make sure JIT is available on the current machine
llvm.check_jit_execution()

def _create_execution_engine():
    """
    Create an ExecutionEngine suitable for JIT code generation on
    the host CPU.  The engine is reusable for an arbitrary number of
    modules.
    """
    # Create a target machine representing the host
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    # And an execution engine with an empty backing module
    backing_mod = llvm.parse_assembly("")
    engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
    return engine

_engine = _create_execution_engine()


def exec(mod):

    global _engine

    """ Execute the main function inside the given module """

    _engine.add_module(mod)
    _engine.finalize_object()

    # Look up the function pointer of the main
    func_ptr = _engine.get_function_address("main")

    # Run the function via ctypes
    cfunc = CFUNCTYPE(c_double)(func_ptr)
    result = cfunc()

    _engine.remove_module(mod)
    return result
