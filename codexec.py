from ctypes import CFUNCTYPE, c_double
from collections import namedtuple
import colorama ; colorama.init()
from termcolor import colored, cprint

from ast import *
from parsing import *
from codegen import *
from lexing.source import Source

Result = namedtuple("Result", ['value', 'ast', 'rawIR', 'optIR'])

_count = 0
_ANONYMOUS = "anonymous"

def make_unique_anonymous_function(ast):
    global _count
    _count += 1
    return Function(proto=Prototype(_ANONYMOUS + str(_count), []), body=ast)

def dump(str, filename):
    """Dump a string to a file name."""
    with open(filename, 'w') as file:
        file.write(str)

def lastIR(module, index = -1):
    """Returns the last bunch of code added to a module. 
    Thus gets the lastly generated IR for the top-level expression"""
    return str(module).split('\n\n')[index]

class KaleidoscopeEvaluator(object):
    """Evaluator for Kaleidoscope expressions.
    Once an object is created, calls to evaluate() add new expressions to the
    module. Definitions (including externs) are only added into the IR - no
    JIT compilation occurs. When a toplevel expression is evaluated, the whole
    module is JITed and the result of the expression is returned.
    """
    def __init__(self, basiclib_file = None):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.basiclib_file = basiclib_file
        self.target = llvm.Target.from_default_triple()
        self.reset()

    def reset(self, history = []):
        self._reset_base();

        if self.basiclib_file:
            # Load basic language library
            try:
                with open(self.basiclib_file) as file:
                    for result in self.eval_generator(Source(self.basiclib_file, file.read())): pass
            except (FileNotFoundError, ParseError, CodegenError) as err:
                print(colored("Could not charge basic library:", 'red'), self.basiclib_file)
                self._reset_base()
                raise

        if history:       
            # Run history 
            try:
                for ast in history: 
                    self._eval_ast(ast)
            except CodegenError:
                print(colored("Could not run history:", 'red'), self.basiclib_file)
                self._reset_base()

    def _reset_base(self):
        self.codegen = LLVMCodeGenerator()
        self._add_builtins(self.codegen.module)

    def evaluate(self, codestr, options = dict()):
        """Evaluates only the first top level expression in codestr.
        Assume there is only one expression. Used by unit tests only. 
        To evaluate all expressions, use eval_generator."""
        return next(self.eval_generator(Source("test", codestr), options)).value

    def eval_generator(self, source, options = dict()):
        """Iterator that evaluates all top level expression in source.
        Yield a namedtuple Result with None for definitions and externs, and the evaluated expression
        value for toplevel expressions.
        """
        for ast in Parser().parse_generator(source):
            yield self._eval_ast(ast, **options)

    def _eval_ast(self, ast, optimize=True, llvmdump=False, noexec = False, parseonly = False, verbose = False):
        """ 
        Evaluate a single top level expression given in ast form
        
            optimize: activate optimizations

            llvmdump: generated IR and assembly code will be dumped prior to execution.

            noexec: the code will be generated but not executed. Yields non-optimized IR.

            parseonly: the code will only be parsed. Yields an AST dump.

            verbose: yields a quadruplet tuple: result, AST, non-optimized IR, optimized IR
        
        """
        rawIR = None
        optIR = None
        if parseonly:
            return Result(ast.dump(), ast, rawIR, optIR)

        # If ast is an expression, enclose it in an anonymous function call with no args to be fetchable from the JIT and callable and runnable afterwards.
        is_expr = isinstance(ast, Expr)     
        if is_expr:
            ast = make_unique_anonymous_function(ast)

        # Generate code
        self.codegen.generate_code(ast)
        if noexec or verbose:
            rawIR = lastIR(self.codegen.module)

        if noexec:
            return Result(rawIR, ast, rawIR, optIR)

        if llvmdump: 
            dump(str(self.codegen.module), '__dump__unoptimized.ll')

        # If we're evaluating a definition or extern declaration, don't do
        # anything else. If we're evaluating an anonymous wrapper for a toplevel
        # expression, JIT-compile the module and run the function to get its
        # result.
        if not is_expr and not verbose:
            return Result(None, ast, rawIR, optIR)

        # Convert LLVM IR into in-memory representation and verify the code
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

        if verbose:
            optIR = lastIR(llvmmod, -2)
            if not is_expr:
                return Result(None, ast, rawIR, optIR)

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
            return Result(result, ast, rawIR, optIR) 

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
        e = KaleidoscopeEvaluator()
        e.evaluate('''
            def oddlessthan(n)
                for x = 1.0, x < n, x + 2 in x
        ''')
        self.assertEqual(e.evaluate('oddlessthan(100)'), 101)
        self.assertEqual(e.evaluate('oddlessthan(1000)'), 1001)
        self.assertEqual(e.evaluate('oddlessthan(0)'), 1)

    def test_custom_binop(self):
        e = KaleidoscopeEvaluator()
        e.evaluate('def binary%(a b) a - b')
        self.assertEqual(e.evaluate('10 % 5'), 5)
        self.assertEqual(e.evaluate('100 % 5.5'), 94.5)

    def test_custom_unop(self):
        e = KaleidoscopeEvaluator()
        e.evaluate('def unary!(a) 0 - a')
        e.evaluate('def unary^(a) a * a')
        self.assertEqual(e.evaluate('!10'), -10)
        self.assertEqual(e.evaluate('^10'), 100)
        self.assertEqual(e.evaluate('!^10'), -100)
        self.assertEqual(e.evaluate('^!10'), 100)

    def test_mixed_ops(self):
        e = KaleidoscopeEvaluator()
        e.evaluate('def unary!(a) 0 - a')
        e.evaluate('def unary^(a) a * a')
        e.evaluate('def binary%(a b) a - b')
        self.assertEqual(e.evaluate('!10 % !20'), 10)
        self.assertEqual(e.evaluate('^(!10 % !20)'), 100)

    def test_var_expr1(self):
        e = KaleidoscopeEvaluator()
        e.evaluate('''
            def foo(x y z)
                var s1 = x + y, s2 = z + y in
                    s1 * s2
            ''')
        self.assertEqual(e.evaluate('foo(1, 2, 3)'), 15)

    def test_var_expr2(self):
        e = KaleidoscopeEvaluator()
        e.evaluate('def binary: (x y) y')
        e.evaluate('''
            def foo(step)
                var accum in
                    (for i = 0, i < 10, i + step in
                        accum = accum + i) 
                    : accum
            ''')
        self.assertEqual(e.evaluate('foo(2)'), 20)

    def test_nested_var_exprs(self):
        e = KaleidoscopeEvaluator()
        e.evaluate('''
            def foo(x y z)
                var s1 = x + y, s2 = z + y in
                    var s3 = s1 * s2 in
                        s3 * 100
            ''')
        self.assertEqual(e.evaluate('foo(1, 2, 3)'), 1500)

    def test_assignments(self):
        e = KaleidoscopeEvaluator()
        e.evaluate('def binary: (x y) y')
        e.evaluate('''
            def foo(a b)
                var s, p, r in
                   s = a + b :
                   p = a * b :
                   r = s + 100 * p :
                   r
            ''')
        self.assertEqual(e.evaluate('foo(2, 3)'), 605)
        self.assertEqual(e.evaluate('foo(10, 20)'), 20030)

    def test_triple_assignment(self):
        e = KaleidoscopeEvaluator()
        e.evaluate('def binary: (x y) y')
        e.evaluate('''
            def foo(a)
                var x, y, z in
                   x = y = z = a 
                   : x + 2 * y + 3 * z
            ''')
        self.assertEqual(e.evaluate('foo(5)'), 30)

if __name__ == '__main__':

    import sys
    if sys.argv[1:] == ['--repl']:
        import kal
        kal.run()
    else:
        unittest.main()
