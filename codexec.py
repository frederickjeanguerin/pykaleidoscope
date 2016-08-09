from ctypes import CFUNCTYPE, c_double
from ast import *
from parsing import *
from codegen import *

class KaleidoscopeEvaluator(object):
    """Evaluator for Kaleidoscope expressions.
    Once an object is created, calls to evaluate() add new expressions to the
    module. Definitions (including externs) are only added into the IR - no
    JIT compilation occurs. When a toplevel expression is evaluated, the whole
    module is JITed and the result of the expression is returned.
    """
    def __init__(self):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.codegen = LLVMCodeGenerator()

        self.target = llvm.Target.from_default_triple()

    def evaluate(self, codestr, optimize=True, llvmdump=False):
        """Evaluate code in codestr.
        Returns None for definitions and externs, and the evaluated expression
        value for toplevel expressions.
        """
        # Parse the given code and generate code from it
        ast = Parser().parse_toplevel(codestr)
        self.codegen.generate_code(ast)

        if llvmdump:
            print('======== Unoptimized LLVM IR')
            print(str(self.codegen.module))

        # If we're evaluating a definition or extern declaration, don't do
        # anything else. If we're evaluating an anonymous wrapper for a toplevel
        # expression, JIT-compile the module and run the function to get its
        # result.
        if not (isinstance(ast, Function) and ast.is_anonymous()):
            return None

        # Convert LLVM IR into in-memory representation
        llvmmod = llvm.parse_assembly(str(self.codegen.module))

        # Optimize the module
        if optimize:
            pmb = llvm.create_pass_manager_builder()
            pmb.opt_level = 2
            pm = llvm.create_module_pass_manager()
            pmb.populate(pm)
            pm.run(llvmmod)

            if llvmdump:
                print('======== Optimized LLVM IR')
                print(str(llvmmod))

        # Create a MCJIT execution engine to JIT-compile the module. Note that
        # ee takes ownership of target_machine, so it has to be recreated anew
        # each time we call create_mcjit_compiler.
        target_machine = self.target.create_target_machine()
        with llvm.create_mcjit_compiler(llvmmod, target_machine) as ee:
            ee.finalize_object()

            if llvmdump:
                print('======== Machine code')
                print(target_machine.emit_assembly(llvmmod))

            fptr = CFUNCTYPE(c_double)(ee.get_function_address(ast.proto.name))

            result = fptr()
            return result


#---- Some unit tests ----#

import unittest

class TestEvaluator(unittest.TestCase):
    def test_basic(self):
        e = KaleidoscopeEvaluator()
        self.assertEqual(e.evaluate('3'), 3.0)
        self.assertEqual(e.evaluate('3+3*4'), 15.0)

    def test_use_func(self):
        e = KaleidoscopeEvaluator()
        self.assertIsNone(e.evaluate('def adder(x y) x+y'))
        self.assertEqual(e.evaluate('adder(5, 4) + adder(3, 2)'), 14.0)

    def test_use_libc(self):
        e = KaleidoscopeEvaluator()
        self.assertIsNone(e.evaluate('extern ceil(x)'))
        self.assertEqual(e.evaluate('ceil(4.5)'), 5.0)
        self.assertIsNone(e.evaluate('extern floor(x)'))
        self.assertIsNone(e.evaluate('def cfadder(x) ceil(x) + floor(x)'))
        self.assertEqual(e.evaluate('cfadder(3.14)'), 7.0)

if __name__ == '__main__':
    import sys
    import colorama
    from termcolor import colored
    colorama.init()
    k = KaleidoscopeEvaluator()
    if len(sys.argv) <= 1 :
        # Example of how to define a couple of functions and then evaluate
        # expressions involving them. A single KaleidoscopeEvaluator object retains
        # its state across multiple calls to 'evaluate'.
        print(k.evaluate('def adder(a b) a + b'))
        print(k.evaluate('def foo(x) (1+2+x)*(x+(1+2))'))
        print(k.evaluate('foo(3)'))
        print(k.evaluate('foo(adder(3, 3)*4)', optimize=True, llvmdump=True))
    else:
        # Simple REPL loop
        command = ' '.join(sys.argv[1:])
        while not command in ['exit', 'quit']:
            try:
                print(colored(k.evaluate(command), 'green'))
            except ParseError as err:
                print(colored('Parse error: ' + str(err), "red"))                    
            except CodegenError as err:
                print(colored('Eval error: ' + str(err), 'red'))
            print("K> ", end="")
            command = input()
            