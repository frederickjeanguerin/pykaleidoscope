from ctypes import CFUNCTYPE, c_double
from ast import *
from parsing import *
from codegen import *

def dump(str, filename):
    with open(filename, 'w') as file:
        file.write(str)

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
        self._add_builtins(self.codegen.module)
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
            dump(str(self.codegen.module), '__dump__unoptimized.ll')

        # If we're evaluating a definition or extern declaration, don't do
        # anything else. If we're evaluating an anonymous wrapper for a toplevel
        # expression, JIT-compile the module and run the function to get its
        # result.
        if not (isinstance(ast, Function) and ast.is_anonymous()):
            return None

        # Convert LLVM IR into in-memory representation
        llvmmod = llvm.parse_assembly(str(self.codegen.module))
        llvmmod.verify()

        # Optimize the module
        if optimize:
            pmb = llvm.create_pass_manager_builder()
            pmb.opt_level = 2
            pm = llvm.create_module_pass_manager()
            pmb.populate(pm)
            pm.run(llvmmod)

            if llvmdump:
                dump(str(llvmmod), '__dump__optimized.ll')

        # Create a MCJIT execution engine to JIT-compile the module. Note that
        # ee takes ownership of target_machine, so it has to be recreated anew
        # each time we call create_mcjit_compiler.
        target_machine = self.target.create_target_machine()
        with llvm.create_mcjit_compiler(llvmmod, target_machine) as ee:
            ee.finalize_object()

            if llvmdump:
                dump(target_machine.emit_assembly(llvmmod), '__dump__assembler.asm')
                print(colored("Code dumped in local directory", 'yellow'))

            fptr = CFUNCTYPE(c_double)(ee.get_function_address(ast.proto.name))

            result = fptr()
            return result

    def _add_builtins(self, module):
        # The C++ tutorial adds putchard() simply by defining it in the host C++
        # code, which is then accessible to the JIT. It doesn't work as simply
        # for us; but luckily it's very easy to define new "C level" functions
        # for our JITed code to use - just emit them as LLVM IR. This is what
        # this method does.

        # Add the declaration of putchar
        putchar_ty = ir.FunctionType(ir.IntType(32), [ir.IntType(32)])
        putchar = ir.Function(module, putchar_ty, 'putchar')

        # Add putchard
        putchard_ty = ir.FunctionType(ir.DoubleType(), [ir.DoubleType()])
        putchard = ir.Function(module, putchard_ty, 'putchard')
        irbuilder = ir.IRBuilder(putchard.append_basic_block('entry'))
        ival = irbuilder.fptoui(putchard.args[0], ir.IntType(32), 'intcast')
        irbuilder.call(putchar, [ival])
        irbuilder.ret(ir.Constant(ir.DoubleType(), 0))


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

    def test_basic_if(self):
        e = KaleidoscopeEvaluator()
        e.evaluate('def foo(a b) a * if a < b then a + 1 else b + 1')
        self.assertEqual(e.evaluate('foo(3, 4)'), 12)
        self.assertEqual(e.evaluate('foo(5, 4)'), 25)

    def test_nested_if(self):
        e = KaleidoscopeEvaluator()
        e.evaluate('''
            def foo(a b c)
                if a < b
                    then if a < c then a * 2 else c * 2
                    else b * 2''')
        self.assertEqual(e.evaluate('foo(1, 20, 300)'), 2)
        self.assertEqual(e.evaluate('foo(10, 2, 300)'), 4)
        self.assertEqual(e.evaluate('foo(100, 2000, 30)'), 60)

    def test_nested_if2(self):
        e = KaleidoscopeEvaluator()
        e.evaluate('''
            def min3(a b c)
                if a < b
                    then if a < c 
                        then a 
                        else c
                    else if b < c
                        then b 
                        else c
            ''')
        self.assertEqual(e.evaluate('min3(1, 2, 3)'), 1)
        self.assertEqual(e.evaluate('min3(1, 3, 2)'), 1)
        self.assertEqual(e.evaluate('min3(2, 1, 3)'), 1)
        self.assertEqual(e.evaluate('min3(2, 3, 1)'), 1)
        self.assertEqual(e.evaluate('min3(3, 1, 2)'), 1)
        self.assertEqual(e.evaluate('min3(3, 3, 2)'), 2)
        self.assertEqual(e.evaluate('min3(3, 3, 3)'), 3)


    def test_for(self):
        # For doesn't return anything, so just make sure evaluating it doesn't
        # crash.
        e = KaleidoscopeEvaluator()
        e.evaluate('''
            def foo(a b c)
                if a < b
                    then for x = 1.0, x < b, c in x+a+c*b
                    else c * 2''')
        self.assertEqual(e.evaluate('foo(1, 2, 3)'), 0)
        self.assertEqual(e.evaluate('foo(3, 2, 30)'), 60)




if __name__ == '__main__':

    import sys
    import colorama
    from termcolor import colored
    colorama.init()
    k = KaleidoscopeEvaluator()

    def print_eval(command, options = dict()):
        try:
            print(colored(k.evaluate(command, **options), 'green'))
        except ParseError as err:
            print(colored('Parse error: ' + str(err), "red"))                    
        except CodegenError as err:
            print(colored('Eval error: ' + str(err), 'red'))
        except RuntimeError as err:
            print(colored('Eval error: ' + str(err), 'red'))
                

    commands = [
        'def add(a b) a + b',
        'add(1, 2)',
        'add(add(1,2), add(3,4))',
        'def max(a b) if a < b then b else a',
        'max(1,2)',        
        'max(max(1,2), max(3,4))',
        'def factorial(n) if n < 2 then 1 else n * factorial(n-1)',
        'factorial(5)',
        'def alphabet(a b) for x = 64 + a, x < 64 + b in putchard(x)',
        'alphabet(1,26)'        
    ]

    if len(sys.argv) >= 2 :
        print_eval(' '.join(sys.argv[1:]))

    else :
        # Execute all predefined commands
        for command in commands:
            print('K>', command)
            print_eval(command)

        # Then enter a simple REPL loop
        print(colored('Type exit or quit to stop the program', 'yellow'))
        options = {
            'optimize' : True,
            'llvmdump' : False
        }
        command = ""
        while not command in ['exit', 'quit']:
            if command in options:
                options[command] = not options[command]
                print(command, '=', options[command])
            elif command :  
                print_eval(command, options)
            print("K> ", end="")
            command = input().strip()
