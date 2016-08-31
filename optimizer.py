import llvmlite.binding as llvm

def optimize(codegen):

    # Convert LLVM IR into in-memory representation and verify the code
    llvmmod = llvm.parse_assembly(str(codegen))
    llvmmod.verify()

    # Optimize the module
    pmb = llvm.create_pass_manager_builder()
    pmb.opt_level = 2
    pm = llvm.create_module_pass_manager()
    pmb.populate(pm)
    pm.run(llvmmod)

    return llvmmod    
    