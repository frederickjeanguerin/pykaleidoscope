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
    program = 'def add(a b) a + b'
    if len(sys.argv) > 1 :
        program = ' '.join(sys.argv[1:])
    print("\nPROGRAM: ", program)        
    ast = Parser().parse_toplevel(program)

    print("\nAST:\n", ast.dump())

    codegen = LLVMCodeGenerator()
    codegen.generate_code(ast)

    print('\nLLVM IR (unoptimized) :')
    print(str(codegen.module))
