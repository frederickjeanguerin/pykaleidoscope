from ast import *
import llvmlite.ir as ir
import llvmlite.binding as llvm

class CodegenError(Exception): pass

class LLVMCodeGenerator(object):
    def __init__(self):
        """Initialize the code generator.
        This creates a new LLVM module into which code is generated. The
        generate_code() method can be called multiple times. It adds the code
        generated for this node into the module, and returns the IR value for
        the node.
        At any time, the current LLVM module being constructed can be obtained
        from the module attribute.
        """
        self.module = ir.Module()

        # Current IR builder.
        self.builder = None

        # Manages a symbol table while a function is being codegen'd. Maps var
        # names to ir.Value.
        self.func_symtab = {}

    def generate_code(self, node):
        assert isinstance(node, (Prototype, Function))
        return self._codegen(node)

    def _codegen(self, node):
        """Node visitor. Dispatches upon node type.
        For AST node of class Foo, calls self._codegen_Foo. Each visitor is
        expected to return a llvmlite.ir.Value.
        """
        method = '_codegen_' + node.__class__.__name__
        return getattr(self, method)(node)

    def _codegen_Number(self, node):
        return ir.Constant(ir.DoubleType(), float(node.val))

    def _codegen_Variable(self, node):
        return self.func_symtab[node.name]

    def _codegen_Binary(self, node):
        lhs = self._codegen(node.lhs)
        rhs = self._codegen(node.rhs)

        if node.op == '+':
            return self.builder.fadd(lhs, rhs, 'addtmp')
        elif node.op == '-':
            return self.builder.fsub(lhs, rhs, 'subtmp')
        elif node.op == '*':
            return self.builder.fmul(lhs, rhs, 'multmp')
        elif node.op == '<':
            cmp = self.builder.fcmp_unordered('<', lhs, rhs, 'cmptmp')
            return self.builder.uitofp(cmp, ir.DoubleType(), 'booltmp')
        else:
            raise CodegenError('Unknown binary operator', node.op)

    def _codegen_If(self, node):
        # Emit comparison value
        cond_val = self._codegen(node.cond_expr)
        cmp = self.builder.fcmp_ordered(
            '!=', cond_val, ir.Constant(ir.DoubleType(), 0.0), 'notnull')

        # Create basic blocks to express the control flow
        then_bb = ir.Block(self.builder.function, 'then')
        else_bb = ir.Block(self.builder.function, 'else')
        merge_bb = ir.Block(self.builder.function, 'endif')

        # branch to either then_bb or else_bb depending on cmp. 
        self.builder.cbranch(cmp, then_bb, else_bb)

        # Emit the 'then' part
        self.builder.function.basic_blocks.append(then_bb)
        self.builder.position_at_start(then_bb)
        then_val = self._codegen(node.then_expr)
        self.builder.branch(merge_bb)
        # Emission of then_val could have generated a new basic block 
        # (and thus modified the current basic block). 
        # To properly set up the PHI, remember which block the 'then' part ends in.
        then_bb = self.builder.block

        # Emit the 'else' part
        self.builder.function.basic_blocks.append(else_bb)
        self.builder.position_at_start(else_bb)
        else_val = self._codegen(node.else_expr)
        self.builder.branch(merge_bb)
        else_bb = self.builder.block

        # Emit the merge ('ifcnt') block
        self.builder.function.basic_blocks.append(merge_bb)
        self.builder.position_at_start(merge_bb)
        phi = self.builder.phi(ir.DoubleType(), 'ifval')
        phi.add_incoming(then_val, then_bb)
        phi.add_incoming(else_val, else_bb)
        return phi

        
    def _codegen_For(self, node):
        # Output this as:
        #   ...
        #   start = startexpr
        #   goto loop
        # loop:
        #   variable = phi [start, loopheader], [nextvariable, loopend]
        #   ...
        #   bodyexpr
        #   ...
        # loopend:
        #   step = stepexpr
        #   nextvariable = variable + step
        #   endcond = endexpr
        #   br endcond, loop, endloop
        # outloop:

        # Emit the start expr first, without the variable in scope.
        start_val = self._codegen(node.start_expr)
        preheader_bb = self.builder.block
        loop_bb = self.builder.function.append_basic_block('loop')

        # Insert an explicit fall through from the current block to loop_bb
        self.builder.branch(loop_bb)
        self.builder.position_at_start(loop_bb)

        # Start the PHI node with an entry for start
        phi = self.builder.phi(ir.DoubleType(), node.id_name)
        phi.add_incoming(start_val, preheader_bb)

        # Within the loop, the variable is defined equal to the PHI node. If it
        # shadows an existing variable, we have to restore it, so save it now.
        oldval = self.func_symtab.get(node.id_name)
        self.func_symtab[node.id_name] = phi

        # Emit the body of the loop. This, like any other expr, can change the
        # current BB. Note that we ignore the value computed by the body.
        body_val = self._codegen(node.body)

        # Increment the counter
        if node.step_expr is None:
            stepval = ir.Constant(ir.DoubleType(), 1.0)
        else:
            stepval = self._codegen(node.step_expr)
        nextvar = self.builder.fadd(phi, stepval, 'nextvar')

        # Compute the end condition
        endcond = self._codegen(node.end_expr)
        cmp = self.builder.fcmp_ordered(
            '!=', endcond, ir.Constant(ir.DoubleType(), 0.0),
            'loopcond')


        # Create the 'after loop' block
        after_bb = ir.Block(self.builder.function, 'after')
        # Insert the conditional branch into the end of loop_end_bb
        self.builder.cbranch(cmp, loop_bb, after_bb)

        # Add a new entry to the PHI node for the backedge
        loop_end_bb = self.builder.block
        phi.add_incoming(nextvar, loop_end_bb)

        # New code will be inserted into after_bb
        self.builder.function.basic_blocks.append(after_bb)
        self.builder.position_at_start(after_bb)

        # Remove the loop variable from the symbol table; if it shadowed an
        # existing variable, restore that.
        if oldval is None:
            del self.func_symtab[node.id_name]
        else:
            self.func_symtab[node.id_name] = oldval

        # The 'for' expression returns the last nextvar
        # return ir.Constant(ir.DoubleType(), 0.0)
        return nextvar

    def _codegen_Call(self, node):
        callee_func = self.module.globals.get(node.callee, None)
        if callee_func is None or not isinstance(callee_func, ir.Function):
            raise CodegenError('Call to unknown function', node.callee)
        if len(callee_func.args) != len(node.args):
            raise CodegenError('Call argument length mismatch', node.callee)
        call_args = [self._codegen(arg) for arg in node.args]
        return self.builder.call(callee_func, call_args, 'calltmp')

    def _codegen_Prototype(self, node):
        funcname = node.name
        # Create a function type
        functype = ir.FunctionType(ir.DoubleType(),
                                  [ir.DoubleType()] * len(node.argnames))

        # If a function with this name already exists in the module...
        if funcname in self.module.globals:
            # We only allow the case in which a declaration exists and now the
            # function is defined (or redeclared) with the same number of args.
            func = existing_func = self.module.globals[funcname]
            if not isinstance(existing_func, ir.Function):
                raise CodegenError('Function/Global name collision', funcname)
            if not existing_func.is_declaration:
                raise CodegenError('Redifinition of {0}'.format(funcname))
            if len(existing_func.function_type.args) != len(functype.args):
                raise CodegenError(
                    'Redifinition with different number of arguments')
        else:
            # Otherwise create a new function
            func = ir.Function(self.module, functype, self.module.get_unique_name(funcname))
        # Set function argument names from AST
        for i, arg in enumerate(func.args):
            arg.name = node.argnames[i]
            self.func_symtab[arg.name] = arg
        return func

    def _codegen_Function(self, node):
        # Reset the symbol table. Prototype generation will pre-populate it with
        # function arguments.
        self.func_symtab = {}
        # Create the function skeleton from the prototype.
        func = self._codegen(node.proto)
        # Create the entry BB in the function and set the builder to it.
        bb_entry = func.append_basic_block('entry')
        self.builder = ir.IRBuilder(bb_entry)
        retval = self._codegen(node.body)
        self.builder.ret(retval)
        return func


if __name__ == '__main__':
    import sys
    from parsing import *
    programs = [
        'def add(a b) a + b',
        'def max(a b) if a < b then b else a',
        'def looping(a b) for i = a, b, 1 in i + 1'
    ]
    if len(sys.argv) > 1 :
        programs = [' '.join(sys.argv[1:])]
    for program in programs:    
        print("\nPROGRAM: ", program)        
        ast = Parser().parse_toplevel(program)

        print("\nAST:\n", ast.dump())

        codegen = LLVMCodeGenerator()
        codegen.generate_code(ast)

        print('\nLLVM IR (unoptimized) :')
        print(str(codegen.module))
        print('\n')