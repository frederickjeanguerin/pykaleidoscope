from ast import *
import llvmlite.ir as ir
import llvmlite.binding as llvm


def irdouble(pyval):
    """Converts a python value into an IR double constant value"""
    return ir.Constant(ir.DoubleType(), pyval)

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

    def _alloca(self, name):
        """Create an alloca in the entry BB of the current function."""
        with self.builder.goto_entry_block():
            alloca = self.builder.alloca(ir.DoubleType(), size=None, name=name)
        return alloca

    def _codegen(self, node):
        """Node visitor. Dispatches upon node type.
        For AST node of class Foo, calls self._codegen_Foo. Each visitor is
        expected to return a llvmlite.ir.Value.
        """
        method = '_codegen_' + node.__class__.__name__
        return getattr(self, method)(node)

    def _codegen_Number(self, node):
        return irdouble(float(node.val))

    def _varaddr(self, varname):
        try:
            return self.func_symtab[varname]
        except KeyError:
            raise CodegenError("Undefined variable: " + varname)    
            

    def _codegen_Variable(self, node):
        return self.builder.load(self._varaddr(node.name), node.name)

    def _codegen_Assignment(self, lhs, rhs):
        if not isinstance(lhs, Variable):
            raise CodegenError('lhs of "=" must be a variable')
        value = self._codegen(rhs)
        self.builder.store(value, self._varaddr(lhs.name))
        return value

    def _codegen_Binary(self, node):

        # Assignment is handled specially because it doesn't follow the general
        # recipe of binary ops.
        if node.op == '=':
            return self._codegen_Assignment(node.lhs, node.rhs)

        lhs = self._codegen(node.lhs)
        rhs = self._codegen(node.rhs)

        if node.op == '+':
            return self.builder.fadd(lhs, rhs, 'addop')
        elif node.op == '-':
            return self.builder.fsub(lhs, rhs, 'subop')
        elif node.op == '*':
            return self.builder.fmul(lhs, rhs, 'multop')
        elif node.op == '<':
            cmp = self.builder.fcmp_unordered('<', lhs, rhs, 'ltop')
            return self.builder.uitofp(cmp, ir.DoubleType(), 'ltoptodouble')
        else:
            # Note one of the predefined operators, so it must be a user-defined one.
            # Emit a call to it.
            func = self.module.get_global('binary{0}'.format(node.op))
            if func is None:
                raise CodegenError('Unknown binary operator', node.op)
            return self.builder.call(func, [lhs, rhs], 'userbinop')    


    def _codegen_If(self, node):
        # Emit comparison value
        cond_val = self._codegen(node.cond_expr)
        cmp = self.builder.fcmp_ordered(
            '!=', cond_val, irdouble(0.0), 'notnull')

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

        # Emit the merge block
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
        #   goto loopcond
        # loopcond:
        #   variable = phi [start, loopheader], [nextvariable, loopbody]
        #   step = stepexpr (or variable + 1)
        #   nextvariable = step
        #   endcond = endexpr
        #   br endcond, loopbody, loopafter
        # loopbody:
        #   bodyexpr
        #   jmp loopcond
        # loopafter:
        #   return variable

        # Define blocks
        loopcond_bb = ir.Block(self.builder.function, 'loopcond')
        loopbody_bb = ir.Block(self.builder.function, 'loopbody')
        loopafter_bb = ir.Block(self.builder.function, 'loopafter')

        # ###########
        # loop header 
        #############

        # Allocate the variable on the stack
        var_addr = self._alloca(node.id_name)

        # Evaluate the starting value for the counter and store it
        start_val = self._codegen(node.start_expr)
        self.builder.store(start_val, var_addr)

        # Save the current block to tell the loop cond where we are coming from
        loopheader_bb = self.builder.block

        # Jump to loop cond
        self.builder.branch(loopcond_bb)

        
        ###########
        # loop cond
        ###########

        self.builder.function.basic_blocks.append(loopcond_bb)
        self.builder.position_at_start(loopcond_bb)

        # Set the symbol table to to reach de local counting variable. 
        # If it shadows an existing variable, save it before and restore it later.
        oldval = self.func_symtab.get(node.id_name)
        self.func_symtab[node.id_name] = var_addr

        # Compute the end condition
        endcond = self._codegen(node.end_expr)
        cmp = self.builder.fcmp_ordered( '!=', endcond, irdouble(0.0), 'loopcond')

        # Goto loop body if condition satisfied, otherwise, exit.
        self.builder.cbranch(cmp, loopbody_bb, loopafter_bb)


        ############
        # loop body
        ############

        self.builder.function.basic_blocks.append(loopbody_bb)
        self.builder.position_at_start(loopbody_bb)

        # Emit the body of the loop. 
        # Note that we ignore the value computed by the body.
        body_val = self._codegen(node.body)

        # If the step is unknown, make it increment by 1
        if node.step_expr is None:
            node.step_expr = Binary("+",Variable(node.id_name), Number(1.0))

        # Evaluate the step and update the counter    
        nextval = self._codegen(node.step_expr)
        self.builder.store(nextval, var_addr)

        # Goto loop cond
        self.builder.branch(loopcond_bb)
        

        #############
        # loop after
        #############

        # New code will be inserted into a new block
        self.builder.function.basic_blocks.append(loopafter_bb)
        self.builder.position_at_start(loopafter_bb)

        # Remove the loop variable from the symbol table; 
        # if it shadowed an existing variable, restore that.
        if oldval is None:
            del self.func_symtab[node.id_name]
        else:
            self.func_symtab[node.id_name] = oldval

        # The 'for' expression returns the last value of the counter
        return self.builder.load(var_addr)


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
            func = ir.Function(self.module, functype, funcname)
            # Name the arguments
            for i, arg in enumerate(func.args):
                arg.name = node.argnames[i]
        
        return func

    def _codegen_Function(self, node):
        # Reset the symbol table. Prototype generation will pre-populate it with
        # function arguments.
        self.func_symtab = {}
        # Create the function skeleton from the prototype.
        func = self._codegen(node.proto)
        # Create the entry BB in the function and set a new builder to it.
        bb_entry = func.append_basic_block('entry')
        self.builder = ir.IRBuilder(bb_entry)

        # Add all arguments to the symbol table and create their allocas
        for i, arg in enumerate(func.args):
            alloca = self._alloca(arg.name)
            self.builder.store(arg, alloca)
            # We dont shadow existing variables names because there are no global variables...
            assert not self.func_symtab.get(arg.name) and "arg name redefined: " + arg.name
            self.func_symtab[arg.name] = alloca

        # Generate code for the body and then return the result
        retval = self._codegen(node.body)
        self.builder.ret(retval)

    def _codegen_Unary(self, node):
        operand = self._codegen(node.rhs)
        func = self.module.get_global('unary{0}'.format(node.op))
        if not func:
            raise CodegenError("Undefined unary operator: " + node.op)
        return self.builder.call(func, [operand], 'unop')

    def _codegen_VarIn(self, node):
        old_bindings = []

        for name, init in node.vars:
            # Emit the initializer before adding the variable to scope. This
            # prevents the initializer from referencing the variable itself.
            if init is not None:
                init_val = self._codegen(init)
            else:
                init_val = ir.Constant(ir.DoubleType(), 0.0)

            # Create var on stack and initialize it.
            var_addr = self._alloca(name)
            self.builder.store(init_val, var_addr)

            # Put var in symbol table; remember old bindings if any.
            old_bindings.append(self.func_symtab.get(name))
            self.func_symtab[name] = var_addr

        # Now all the vars are in scope. Codegen the body.
        body_val = self._codegen(node.body)

        # Restore the old bindings.
        for i, (name, _) in enumerate(node.vars):
            if old_bindings[i] is not None:
                self.func_symtab[name] = old_bindings[i]
            else:
                del self.func_symtab[name]

        return body_val


if __name__ == '__main__':

    import run
    run.repl(noexec = True) 
    